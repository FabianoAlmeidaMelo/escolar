# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-04-13 00:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0012_auto_20180305_2119'),
    ]

    operations = [
        migrations.AddField(
            model_name='contratoaluno',
            name='bolsa',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Bolsa (%)'),
        ),
    ]
