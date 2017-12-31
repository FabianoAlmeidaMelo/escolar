# coding: utf-8
from django.db import models
from escolar.escolas.models import escolas
from core.models import UserAdd, UserUpd


def escola_contrato_path(instance, logo):
    '''
    escola que fez o upload do arquivo
    file will be uploaded to MEDIA_ROOT/conta_<id>/<filename>
    '''
    return 'escola_{0}/contratos/{1}'.format(instance.nome, contrato)



class ContratoEscola(UserAdd, UserUpd):
    '''
    ref #31
    Contrato faz a ligação:
    Escola + ResponsavelAluno + Aluno
    '''
    escola = models.ForeignKey(Escola)
    responsavel = models.ForeignKey('core.User', related_name='responsavel')
    aluno = models.ForeignKey('core.User', related_name='aluno')
    serie = models.CharField('série', null=True, blank=True)
    curso = models.CharField('curso', null=True, blank=True)
    matricula_nr = models.CharField('Nr da Matrícula', null=True, blank=True)
    data_assinatura = models.DateTimeField('Data assinatura', null=True, blank=True)
    contrato = models.FileField(upload_to=escola_contrato_path, null=True, blank=True)
    valor = models.DecimalField(
        'valor',
        max_digits=7,
        decimal_places=2)
    nr_parcela = models.PositiveSmallIntegerField('Nr de Parcelas')
    matricula_valor  = models.DecimalField('Valor Matrícula',
        max_digits=7,
        decimal_places=2)
    desconto  = models.DecimalField('Desconto',
        max_digits=7,
        decimal_places=2,
        blank=True,
        null=True)

    class Meta:
        verbose_name = 'contrato'
        verbose_name_plural = 'contratos'
        ordering = ('nome',)

    def __str__(self):
        return self.nome
