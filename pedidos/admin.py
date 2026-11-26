from django.contrib import admin

from .models import ItemPedido, Pedido


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = (
        "produto",
        "produto_nome",
        "preco_unitario_centavos",
        "preco_unitario_formatado",
        "quantidade",
        "subtotal_formatado",
    )
    fields = readonly_fields
    can_delete = False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente_nome", "total_formatado", "criado_em")
    search_fields = ("cliente_nome", "itens__produto_nome")
    date_hierarchy = "criado_em"
    readonly_fields = (
        "cliente_nome",
        "total_centavos",
        "total_formatado",
        "criado_em",
    )
    inlines = (ItemPedidoInline,)


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = (
        "pedido",
        "produto_nome",
        "quantidade",
        "preco_unitario_formatado",
        "subtotal_formatado",
    )
    search_fields = ("pedido__cliente_nome", "produto_nome")
    list_select_related = ("pedido", "produto")
    readonly_fields = (
        "pedido",
        "produto",
        "produto_nome",
        "preco_unitario_centavos",
        "preco_unitario_formatado",
        "quantidade",
        "subtotal_formatado",
    )
