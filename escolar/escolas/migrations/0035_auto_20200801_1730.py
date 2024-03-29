# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2020-08-01 20:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escolas', '0034_auto_20180507_2038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aluno',
            name='ano',
            field=models.SmallIntegerField(default=2020),
        ),
        migrations.AlterField(
            model_name='classe',
            name='ano',
            field=models.SmallIntegerField(choices=[(None, '--'), (2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022)], verbose_name='Ano'),
        ),
    ]
