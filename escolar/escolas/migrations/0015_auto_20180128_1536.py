# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-01-28 15:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('escolas', '0014_auto_20180127_0011'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='membrofamilia',
            options={'ordering': ('nome',), 'verbose_name': 'Membro da Família', 'verbose_name_plural': 'Membros da Família'},
        ),
    ]