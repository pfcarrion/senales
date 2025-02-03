# Generated by Django 5.0 on 2025-01-09 22:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_alter_subscription_usuario"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="metodo_pago",
            field=models.CharField(
                choices=[
                    ("paypal", "PayPal"),
                    ("tarjeta", "Tarjeta de crédito por PayPal"),
                    ("binance", "Binance"),
                ],
                default="paypal",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="subscription",
            name="payer_email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name="subscription",
            name="transaction_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="estado",
            field=models.CharField(
                choices=[
                    ("pendiente", "Pendiente"),
                    ("pagado", "Pagado"),
                    ("suspendido", "Suspendido"),
                    ("cancelado", "Cancelado"),
                    ("finalizado", "Finalizado"),
                ],
                default="pendiente",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="subscription",
            name="usuario",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
