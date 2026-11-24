from django.shortcuts import render

from .models import Produto


def inicio(request):
    produtos = Produto.objects.filter(ativo=True)
    contexto = {"produtos": produtos}
    return render(request, "cardapio/index.html", contexto)
