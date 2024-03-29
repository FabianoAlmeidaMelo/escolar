# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-01-27 00:11
from __future__ import unicode_literals

from django.db import migrations, models
import escolar.escolas.models


class Migration(migrations.Migration):

    dependencies = [
        ('escolas', '0013_aluno_membrofamilia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aluno',
            name='documento',
            field=models.FileField(blank=True, null=True, upload_to=escolar.escolas.models.escola_directory_path, verbose_name='RG e ou CPF'),
        ),
        migrations.AlterField(
            model_name='aluno',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to=escolar.escolas.models.escola_directory_path, verbose_name='Foto'),
        ),
    ]
