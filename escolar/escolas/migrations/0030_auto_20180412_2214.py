# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-04-13 01:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('escolas', '0029_auto_20180410_2216'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='membrofamilia',
            name='parentesco',
        ),
        migrations.RemoveField(
            model_name='membrofamilia',
            name='responsavel_financeiro',
        ),
        migrations.RemoveField(
            model_name='membrofamilia',
            name='responsavel_pedagogico',
        ),
    ]
