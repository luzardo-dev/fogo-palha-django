from django.urls import path

from . import views

app_name = "pedidos"

urlpatterns = [
    path("", views.criar, name="criar"),
    path("<uuid:token_publico>/", views.confirmacao, name="confirmacao"),
]
