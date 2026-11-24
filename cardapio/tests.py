from django.contrib import admin
from django.test import SimpleTestCase, TestCase

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


class AdminTests(SimpleTestCase):
    def test_produto_esta_registrado_na_administracao(self):
        self.assertIn(Produto, admin.site._registry)
