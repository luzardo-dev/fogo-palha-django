from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from cardapio.models import Produto
from pedidos.models import Pedido
from pedidos.servicos import ErroPedido, criar_pedido


@require_POST
def criar(request):
    quantidades = {
        chave.removeprefix("quantidade_"): valor
        for chave, valor in request.POST.items()
        if chave.startswith("quantidade_")
    }
    try:
        pedido = criar_pedido(request.POST.get("cliente_nome", ""), quantidades)
    except ErroPedido as erro:
        produtos = list(Produto.objects.filter(ativo=True))
        for produto in produtos:
            produto.quantidade_informada = quantidades.get(str(produto.pk), "0")
        return render(
            request,
            "cardapio/index.html",
            {
                "produtos": produtos,
                "erro_pedido": str(erro),
                "cliente_nome": request.POST.get("cliente_nome", ""),
            },
            status=400,
        )
    return redirect("pedidos:confirmacao", token_publico=pedido.token_publico)


def confirmacao(request, token_publico):
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related("itens"), token_publico=token_publico
    )
    return render(request, "pedidos/confirmacao.html", {"pedido": pedido})
