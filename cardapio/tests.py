import base64
import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings

from cardapio import regras
from cardapio.models import Produto


class ProdutoTests(SimpleTestCase):
    def test_campos_preservam_o_contrato_das_aulas(self):
        campos = {campo.name: campo for campo in Produto._meta.fields}

        self.assertEqual(campos["nome"].max_length, 120)
        self.assertEqual(
            campos["preco_centavos"].get_internal_type(), "PositiveIntegerField"
        )
        self.assertTrue(campos["ativo"].default)
        self.assertEqual(campos["imagem"].upload_to, "produtos/")
        self.assertTrue(campos["imagem"].blank)

    def test_representacao_textual_usa_o_nome(self):
        produto = Produto(nome="Bolo de milho", preco_centavos=850)

        self.assertEqual(str(produto), "Bolo de milho")

    def test_preco_formatado_exibe_reais_e_centavos(self):
        produto = Produto(nome="Café", preco_centavos=450)

        self.assertEqual(produto.preco_formatado(), "R$ 4,50")


class RegrasTests(SimpleTestCase):
    def test_modulo_mantem_as_funcoes_do_dia_16_e_17(self):
        self.assertTrue(hasattr(regras, "formatar_preco"))
        self.assertTrue(hasattr(regras, "produtos_disponiveis"))

    def test_formatar_preco(self):
        self.assertEqual(regras.formatar_preco(1250), "R$ 12,50")

    def test_produtos_disponiveis_remove_inativos(self):
        produtos = [
            {"nome": "Café", "preco_centavos": 450, "ativo": True},
            {"nome": "Suco", "preco_centavos": 700, "ativo": False},
        ]

        self.assertEqual(regras.produtos_disponiveis(produtos), [produtos[0]])


class CatalogoTests(TestCase):
    def test_pagina_inicial_exibe_somente_produtos_ativos(self):
        Produto.objects.create(nome="Café", preco_centavos=450, ativo=True)
        Produto.objects.create(nome="Suco", preco_centavos=700, ativo=False)

        resposta = self.client.get("/")

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Café")
        self.assertContains(resposta, "R$ 4,50")
        self.assertNotContains(resposta, "Suco")

    def test_pagina_inicial_exibe_mensagem_quando_nao_ha_produtos(self):
        resposta = self.client.get("/")

        self.assertContains(resposta, "Nenhum produto disponível no momento.")

    def test_pagina_exibe_imagem_enviada_e_fallback_sem_imagem(self):
        png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
        )
        upload = SimpleUploadedFile("cafe.png", png, content_type="image/png")

        with tempfile.TemporaryDirectory() as diretorio:
            with override_settings(MEDIA_ROOT=diretorio, MEDIA_URL="/media/"):
                com_imagem = Produto.objects.create(
                    nome="Café", preco_centavos=450, imagem=upload
                )
                Produto.objects.create(nome="Bolo", preco_centavos=850)

                resposta = self.client.get("/")

                self.assertContains(resposta, com_imagem.imagem.url)
                self.assertContains(resposta, "produto-sem-imagem")
                self.assertTrue(Path(com_imagem.imagem.path).is_file())


class ConfiguracaoMediaTests(SimpleTestCase):
    def test_uploads_usam_diretorio_media_local(self):
        self.assertEqual(settings.MEDIA_URL, "/media/")
        self.assertEqual(settings.MEDIA_ROOT, settings.BASE_DIR / "media")


class AdminTests(SimpleTestCase):
    def test_produto_esta_registrado_na_administracao(self):
        self.assertIn(Produto, admin.site._registry)
