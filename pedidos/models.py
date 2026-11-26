import uuid

from django.core.validators import MinValueValidator
from django.db import models

from cardapio.models import Produto
from cardapio.regras import formatar_preco


class Pedido(models.Model):
    token_publico = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    cliente_nome = models.CharField(max_length=120)
    total_centavos = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"

    def __str__(self):
        return f"Pedido {self.pk} — {self.cliente_nome}"

    @property
    def total_calculado_centavos(self):
        return sum(item.subtotal_centavos for item in self.itens.all())

    def total_formatado(self):
        return formatar_preco(self.total_centavos)


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name="itens"
    )
    produto = models.ForeignKey(
        Produto, on_delete=models.SET_NULL, null=True, blank=True
    )
    produto_nome = models.CharField(max_length=120)
    preco_unitario_centavos = models.PositiveIntegerField()
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["id"]
        verbose_name = "item do pedido"
        verbose_name_plural = "itens do pedido"

    def __str__(self):
        return f"{self.quantidade} × {self.produto_nome}"

    @property
    def subtotal_centavos(self):
        return self.preco_unitario_centavos * self.quantidade

    def preco_unitario_formatado(self):
        return formatar_preco(self.preco_unitario_centavos)

    def subtotal_formatado(self):
        return formatar_preco(self.subtotal_centavos)
