# Generated by Django 5.1.1 on 2025-01-27 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_carritohistorial_proveedor_carritoitem_proveedor'),
    ]

    operations = [
        migrations.AddField(
            model_name='proveedor',
            name='activo',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
    ]