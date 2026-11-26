from django.db import models

from .regras import formatar_preco


class Produto(models.Model):
    nome = models.CharField(max_length=120)
    preco_centavos = models.PositiveIntegerField()
    ativo = models.BooleanField(default=True)
    imagem = models.ImageField(upload_to="produtos/", blank=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "produto"
        verbose_name_plural = "produtos"

    def __str__(self):
        return self.nome

    def preco_formatado(self):
        return formatar_preco(self.preco_centavos)
