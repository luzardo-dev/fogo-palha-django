"""Regras de negócio do cardápio.

As funções abaixo mantêm a continuidade com os exemplos dos Dias 16 e 17.
"""


def formatar_preco(preco_centavos):
    reais = preco_centavos // 100
    centavos = preco_centavos % 100
    return f"R$ {reais},{centavos:02d}"


def produtos_disponiveis(produtos):
    return [produto for produto in produtos if produto["ativo"]]
