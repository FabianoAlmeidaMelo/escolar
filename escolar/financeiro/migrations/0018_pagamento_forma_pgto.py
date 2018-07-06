# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-07-06 01:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0017_auto_20180602_1936'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagamento',
            name='forma_pgto',
            field=models.SmallIntegerField(blank=True, choices=[(None, '--'), (1, 'boleto bancário'), (2, 'cartão de crédito'), (3, 'cartão de débito'), (4, 'cheque'), (5, 'dinheiro'), (6, 'permuta'), (7, 'transferência bancária')], null=True, verbose_name='Forma de pagamento'),
        ),
    ]
