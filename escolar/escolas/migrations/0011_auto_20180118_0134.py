# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-01-18 01:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escolas', '0010_auto_20180102_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classe',
            name='ano',
            field=models.SmallIntegerField(choices=[(None, '--'), (2017, 2017), (2018, 2018), (2019, 2019)], verbose_name='Ano'),
        ),
    ]