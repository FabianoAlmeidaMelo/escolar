# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2020-08-08 22:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0020_auto_20200801_1730'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagamento',
            name='data_pag',
            field=models.DateTimeField(blank=True, null=True, verbose_name='data pago:'),
        ),
        migrations.AlterField(
            model_name='pagamento',
            name='data',
            field=models.DateField(blank=True, null=True, verbose_name='data prevista:'),
        ),
    ]
