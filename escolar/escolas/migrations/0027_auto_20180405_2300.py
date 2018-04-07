# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-04-06 02:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import escolar.escolas.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20180309_2232'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('municipios', '0001_initial'),
        ('escolas', '0026_remove_aluno_responsaveis'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pessoa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_add', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_upd', models.DateTimeField(default=django.utils.timezone.now)),
                ('teste', models.CharField(blank=True, max_length=100, null=True)),
                ('celular', models.CharField(blank=True, max_length=11, null=True)),
                ('cpf', models.CharField(blank=True, max_length=14, null=True, verbose_name='CPF')),
                ('documento', models.FileField(blank=True, null=True, upload_to=escolar.escolas.models.escola_aluno_directory_path, verbose_name='RG e ou CPF')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='e-mail')),
                ('nacionalidade', models.CharField(max_length=50)),
                ('nascimento', models.DateField(blank=True, null=True, verbose_name='Data Nascimento')),
                ('nome', models.CharField(max_length=100)),
                ('profissao', models.CharField(blank=True, max_length=100, null=True, verbose_name='Profissão')),
                ('rg', models.CharField(blank=True, max_length=14, null=True, verbose_name='RG')),
                ('sexo', models.SmallIntegerField(verbose_name='Sexo')),
                ('telefone', models.CharField(blank=True, max_length=11, null=True)),
                ('endereco', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Endereco')),
                ('escola', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='escolas.Escola')),
                ('natural_municipio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='municipios.Municipio')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user_add', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='escolas_pessoa_created_by', to=settings.AUTH_USER_MODEL)),
                ('user_upd', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='escolas_pessoa_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='aluno',
            name='documento',
            field=models.FileField(blank=True, null=True, upload_to=escolar.escolas.models.escola_aluno_directory_path, verbose_name='RG e ou CPF'),
        ),
        migrations.AlterField(
            model_name='aluno',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to=escolar.escolas.models.escola_aluno_directory_path, verbose_name='Foto'),
        ),
        migrations.AddField(
            model_name='aluno',
            name='pessoa',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='escolas.Pessoa'),
        ),
        migrations.AddField(
            model_name='membrofamilia',
            name='pessoa',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='escolas.Pessoa'),
        ),
    ]
