# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-02-27 01:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escolas', '0020_auto_20180225_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='escola',
            name='cnpj',
            field=models.CharField(default='85887876', max_length=14, verbose_name='cnpj'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='escola',
            name='razao_social',
            field=models.CharField(default='colegio ltda', max_length=200, verbose_name='razão social'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='aluno',
            name='ra',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='RA'),
        ),
    ]