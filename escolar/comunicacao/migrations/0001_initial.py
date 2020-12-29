# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2020-08-01 20:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('escolas', '0035_auto_20200801_1730'),
    ]

    operations = [
        migrations.CreateModel(
            name='MensagemDefault',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.SmallIntegerField(choices=[(1, 'cobrança'), (2, 'saudação'), (3, 'avisos'), (4, 'conteúdo'), (5, 'outros')], verbose_name='Tipo:')),
                ('titulo', models.CharField(max_length=100, verbose_name='Título: ')),
                ('cabecalho', models.CharField(max_length=100, verbose_name='Cabeçalho: ')),
                ('corpo', models.TextField(verbose_name='Corpo')),
                ('assinatura', models.CharField(max_length=300, verbose_name='Assinatura:')),
                ('escola', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='escolas.Escola')),
            ],
            options={
                'verbose_name': 'Mensagem Default',
                'verbose_name_plural': 'Mensagens Default',
            },
        ),
        migrations.AlterUniqueTogether(
            name='mensagemdefault',
            unique_together=set([('escola', 'tipo')]),
        ),
    ]