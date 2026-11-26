import uuid

from django.db import migrations, models


def preencher_tokens_publicos(apps, schema_editor):
    Pedido = apps.get_model("pedidos", "Pedido")
    for pedido in Pedido.objects.filter(token_publico__isnull=True).iterator():
        pedido.token_publico = uuid.uuid4()
        pedido.save(update_fields=["token_publico"])


class Migration(migrations.Migration):
    dependencies = [
        ("pedidos", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="pedido",
            name="token_publico",
            field=models.UUIDField(editable=False, null=True),
        ),
        migrations.RunPython(preencher_tokens_publicos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="pedido",
            name="token_publico",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
