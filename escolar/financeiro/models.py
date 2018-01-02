# coding: utf-8
from django.db import models
from escolar.escolas.models import Escola, ANO
from escolar.core.models import UserAdd, UserUpd


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
    Escola + Responsavel pelo Aluno + Aluno
    '''
    escola = models.ForeignKey(Escola)
    responsavel = models.ForeignKey('core.User', related_name='contrato_responsavel')
    aluno = models.ForeignKey('core.User', related_name='contrato_aluno')
    serie = models.CharField('série', null=True, blank=True, max_length=20)
    curso = models.CharField('curso', null=True, blank=True, max_length=120)
    ano = models.SmallIntegerField('Ano', choices=ANO)
    matricula_nr = models.CharField('Nr da Matrícula', null=True, blank=True, max_length=20)
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
        #ordering = ('aluno',)

    def __str__(self):
        return self.escola.nome
