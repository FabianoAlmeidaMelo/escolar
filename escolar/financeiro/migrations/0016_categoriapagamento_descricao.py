# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-16 02:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0015_auto_20180502_2317'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoriapagamento',
            name='descricao',
            field=models.CharField(default='x', max_length=150, verbose_name='Descrição'),
            preserve_default=False,
        ),
    ]
