# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-01-07 23:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import escolar.financeiro.models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Movimento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255, verbose_name='Título')),
                ('data_prevista', models.DateField(blank=True, null=True)),
                ('valor', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('num_nf', models.CharField(blank=True, max_length=20, null=True)),
                ('data_nf', models.DateField(blank=True, null=True)),
                ('data_pag', models.DateField(blank=True, null=True)),
                ('efet', models.BooleanField(default=False)),
                ('valor_pag', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('observacao', models.TextField(verbose_name='Observacao')),
                ('tipo', models.SmallIntegerField(blank=True, null=True, verbose_name='Tipo')),
                ('nr_parcela', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Nr de Parcelas')),
                ('nr_documento', models.CharField(blank=True, max_length=20, null=True, verbose_name='Nr Documento')),
            ],
            options={
                'ordering': ('contrato', 'nr_parcela'),
            },
        ),
        migrations.AddField(
            model_name='contratoescola',
            name='ano',
            field=models.SmallIntegerField(default=2018),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contratoescola',
            name='vencimento',
            field=models.IntegerField(default=10, validators=[escolar.financeiro.models.validate_vencimento], verbose_name='Dia de Pagar'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contratoescola',
            name='aluno',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contrato_aluno', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='contratoescola',
            name='date_add',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='contratoescola',
            name='date_upd',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='contratoescola',
            name='responsavel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contrato_responsavel', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='movimento',
            name='contrato',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='financeiro.ContratoEscola'),
        ),
        migrations.AddField(
            model_name='movimento',
            name='parcela',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='financeiro.Movimento'),
        ),
    ]
