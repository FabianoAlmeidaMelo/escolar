# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-03-05 15:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('escolas', '0004_escola_pais'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResponsavelAluno',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(default=django.utils.timezone.now, verbose_name='data de cadastro')),
                ('aluno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aluno_do_responsevel', to=settings.AUTH_USER_MODEL)),
                ('escola', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='escolas.Escola')),
                ('responsavel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responsavel_pelo_aluno', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
