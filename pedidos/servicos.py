from django.db import transaction

from cardapio.models import Produto
from pedidos.models import ItemPedido, Pedido

QUANTIDADE_MAXIMA_POR_PRODUTO = 20


class ErroPedido(ValueError):
    pass


@transaction.atomic
def criar_pedido(cliente_nome, quantidades):
    cliente_nome = cliente_nome.strip()
    if not cliente_nome:
        raise ErroPedido("Informe o nome do cliente.")
    if len(cliente_nome) > 120:
        raise ErroPedido("O nome deve ter até 120 caracteres.")

    selecionados = {}
    for produto_id, valor in quantidades.items():
        try:
            quantidade = int(valor)
            identificador = int(produto_id)
        except (TypeError, ValueError) as erro:
            raise ErroPedido("Quantidade inválida.") from erro
        if quantidade < 0 or quantidade > QUANTIDADE_MAXIMA_POR_PRODUTO:
            raise ErroPedido("Quantidade inválida.")
        if quantidade:
            selecionados[identificador] = quantidade

    if not selecionados:
        raise ErroPedido("Escolha pelo menos um produto.")

    produtos = Produto.objects.select_for_update().in_bulk(selecionados)
    if len(produtos) != len(selecionados) or any(
        not produto.ativo for produto in produtos.values()
    ):
        raise ErroPedido("Produto indisponível.")

    pedido = Pedido.objects.create(cliente_nome=cliente_nome)
    itens = [
        ItemPedido(
            pedido=pedido,
            produto=produto,
            produto_nome=produto.nome,
            preco_unitario_centavos=produto.preco_centavos,
            quantidade=selecionados[produto.pk],
        )
        for produto in produtos.values()
    ]
    ItemPedido.objects.bulk_create(itens)
    pedido.total_centavos = sum(item.subtotal_centavos for item in itens)
    pedido.save(update_fields=["total_centavos"])
    return pedido
