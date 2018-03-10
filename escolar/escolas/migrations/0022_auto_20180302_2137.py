# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-03-03 00:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('escolas', '0021_auto_20180226_2202'),
    ]

    operations = [
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Serie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serie', models.CharField(max_length=30)),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='escolas.Curso')),
            ],
        ),
        migrations.AddField(
            model_name='aluno',
            name='curso',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='escolas.Curso'),
        ),
        migrations.AddField(
            model_name='escola',
            name='cursos',
            field=models.ManyToManyField(to='escolas.Curso'),
        ),
    ]
