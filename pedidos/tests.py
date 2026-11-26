from django.contrib import admin
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from cardapio.models import Produto
from pedidos.models import ItemPedido, Pedido
from pedidos.servicos import ErroPedido, criar_pedido


class ModelosPedidoTests(TestCase):
    def test_item_guarda_snapshot_e_pedido_totaliza_os_itens(self):
        produto = Produto.objects.create(nome="Café", preco_centavos=450)
        pedido = Pedido.objects.create(cliente_nome="Cliente de teste")
        item = ItemPedido.objects.create(
            pedido=pedido,
            produto=produto,
            produto_nome=produto.nome,
            preco_unitario_centavos=produto.preco_centavos,
            quantidade=3,
        )

        self.assertEqual(item.subtotal_centavos, 1350)
        self.assertEqual(pedido.total_calculado_centavos, 1350)
        self.assertEqual(pedido.total_centavos, 0)
        self.assertEqual(str(pedido), f"Pedido {pedido.pk} — Cliente de teste")


class CriarPedidoTests(TestCase):
    def setUp(self):
        self.cafe = Produto.objects.create(nome="Café", preco_centavos=450)
        self.bolo = Produto.objects.create(nome="Bolo", preco_centavos=850)

    def test_cria_pedido_atomico_com_snapshot_e_total_do_banco(self):
        pedido = criar_pedido(
            "  Maria  ", {str(self.cafe.pk): "2", str(self.bolo.pk): "1"}
        )

        self.assertEqual(pedido.cliente_nome, "Maria")
        self.assertEqual(pedido.total_centavos, 1750)
        self.assertEqual(pedido.itens.count(), 2)
        item = pedido.itens.get(produto=self.cafe)
        self.assertEqual(item.produto_nome, "Café")
        self.assertEqual(item.preco_unitario_centavos, 450)
        self.assertEqual(item.quantidade, 2)

    def test_rejeita_pedido_vazio_sem_persistir(self):
        with self.assertRaisesMessage(ErroPedido, "Escolha pelo menos um produto"):
            criar_pedido("Maria", {str(self.cafe.pk): "0"})

        self.assertFalse(Pedido.objects.exists())
        self.assertFalse(ItemPedido.objects.exists())

    def test_rejeita_nome_do_cliente_vazio(self):
        with self.assertRaisesMessage(ErroPedido, "Informe o nome do cliente"):
            criar_pedido("   ", {str(self.cafe.pk): "1"})

        self.assertFalse(Pedido.objects.exists())

    def test_rejeita_quantidade_invalida_sem_persistir(self):
        for quantidade in ("abc", "-1", "1.5", "21", str(2**63)):
            with self.subTest(quantidade=quantidade):
                with self.assertRaisesMessage(ErroPedido, "Quantidade inválida"):
                    criar_pedido("Maria", {str(self.cafe.pk): quantidade})

        self.assertFalse(Pedido.objects.exists())

    def test_rejeita_nome_acima_do_limite_do_modelo(self):
        with self.assertRaisesMessage(ErroPedido, "até 120 caracteres"):
            criar_pedido("M" * 121, {str(self.cafe.pk): "1"})

        self.assertFalse(Pedido.objects.exists())

    def test_rejeita_produto_inativo_sem_persistir(self):
        self.cafe.ativo = False
        self.cafe.save(update_fields=["ativo"])

        with self.assertRaisesMessage(ErroPedido, "Produto indisponível"):
            criar_pedido("Maria", {str(self.cafe.pk): "1"})

        self.assertFalse(Pedido.objects.exists())


class FluxoCompraTests(TestCase):
    def setUp(self):
        self.cafe = Produto.objects.create(nome="Café", preco_centavos=450)
        self.bolo = Produto.objects.create(nome="Bolo", preco_centavos=850)
        self.inativo = Produto.objects.create(
            nome="Suco", preco_centavos=700, ativo=False
        )

    def test_cardapio_exibe_formulario_apenas_para_produtos_ativos(self):
        resposta = self.client.get("/")

        self.assertContains(resposta, reverse("pedidos:criar"))
        self.assertContains(resposta, f'name="quantidade_{self.cafe.pk}"')
        self.assertContains(resposta, f'name="quantidade_{self.bolo.pk}"')
        self.assertNotContains(resposta, f'name="quantidade_{self.inativo.pk}"')
        self.assertContains(resposta, "csrfmiddlewaretoken")

    def test_post_cria_pedido_e_redireciona_para_confirmacao(self):
        resposta = self.client.post(
            reverse("pedidos:criar"),
            {
                "cliente_nome": "Maria",
                f"quantidade_{self.cafe.pk}": "2",
                f"quantidade_{self.bolo.pk}": "1",
            },
        )

        pedido = Pedido.objects.get()
        self.assertRedirects(
            resposta, reverse("pedidos:confirmacao", args=[pedido.token_publico])
        )
        confirmacao = self.client.get(resposta.url)
        self.assertContains(confirmacao, "Pedido confirmado")
        self.assertContains(confirmacao, "Maria")
        self.assertContains(confirmacao, "R$ 17,50")
        self.assertContains(confirmacao, "2 × Café")

    def test_post_invalido_reexibe_cardapio_sem_persistir(self):
        resposta = self.client.post(
            reverse("pedidos:criar"),
            {"cliente_nome": "Maria", f"quantidade_{self.cafe.pk}": "abc"},
        )

        self.assertEqual(resposta.status_code, 400)
        self.assertContains(resposta, "Quantidade inválida", status_code=400)
        self.assertContains(
            resposta,
            f'name="quantidade_{self.cafe.pk}" type="number" min="0" max="20" step="1" value="abc"',
            status_code=400,
        )
        self.assertFalse(Pedido.objects.exists())

    def test_confirmacao_publica_usa_token_nao_enumeravel(self):
        pedido = criar_pedido("Maria", {str(self.cafe.pk): "1"})

        resposta = self.client.get(
            reverse("pedidos:confirmacao", args=[pedido.token_publico])
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertNotEqual(str(pedido.token_publico), str(pedido.pk))
        self.assertNotIn(f"/pedidos/{pedido.pk}/", resposta.request["PATH_INFO"])

    def test_post_exige_csrf(self):
        cliente = Client(enforce_csrf_checks=True)

        resposta = cliente.post(
            reverse("pedidos:criar"),
            {"cliente_nome": "Maria", f"quantidade_{self.cafe.pk}": "1"},
        )

        self.assertEqual(resposta.status_code, 403)


class AdminPedidoTests(SimpleTestCase):
    def test_pedido_e_item_estao_disponiveis_na_administracao(self):
        self.assertIn(Pedido, admin.site._registry)
        self.assertIn(ItemPedido, admin.site._registry)
        pedido_admin = admin.site._registry[Pedido]
        item_admin = admin.site._registry[ItemPedido]
        self.assertTrue(
            any(inline.model is ItemPedido for inline in pedido_admin.inlines)
        )
        self.assertIn("total_centavos", pedido_admin.readonly_fields)
        self.assertIn("preco_unitario_centavos", item_admin.readonly_fields)
