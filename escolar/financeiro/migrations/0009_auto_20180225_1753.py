# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-02-25 20:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0008_parametroscontrato_vencimento'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categoriapagamento',
            options={'ordering': ('nome',)},
        ),
        migrations.AlterField(
            model_name='contratoaluno',
            name='condicao_juros',
            field=models.SmallIntegerField(blank=True, choices=[(None, '--'), (1, 'pro rata die'), (2, 'Por Mês')], null=True, verbose_name='condição juros'),
        ),
        migrations.AlterField(
            model_name='parametroscontrato',
            name='condicao_juros',
            field=models.SmallIntegerField(blank=True, choices=[(None, '--'), (1, 'pro rata die'), (2, 'Por Mês')], null=True, verbose_name='condição juros'),
        ),
    ]
