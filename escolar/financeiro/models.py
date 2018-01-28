# coding: utf-8
from django.db import models
from escolar.escolas.models import ANO
from escolar.core.models import UserAdd, UserUpd
from datetime import date, timedelta


ano_corrente = date.today().year


def escola_contrato_path(instance, logo):
    '''
    escola que fez o upload do arquivo
    file will be uploaded to MEDIA_ROOT/conta_<id>/<filename>
    '''
    return 'escola_{0}/contratos/{1}'.format(instance.nome, contrato)

def validate_vencimento(value):
    if value not in range(1, 29):
        raise ValidationError(u'%s Não está entre 1 e 28' % value)

class ContratoAluno(UserAdd, UserUpd):
    '''
    ref #31
    Contrato faz a ligação:
    Escola + Responsavel pelo Aluno + Aluno
    python manage.py dumpdata financeiro.contratoescola --indent=4
    '''
    responsavel = models.ForeignKey('escolas.MembroFamilia')
    aluno = models.ForeignKey('escolas.Aluno', related_name='contrato_aluno')
    serie = models.CharField('série', null=True, blank=True, max_length=20)
    curso = models.CharField('curso', null=True, blank=True, max_length=120)
    ano = models.SmallIntegerField()
    matricula_nr = models.CharField('Nr da Matrícula', null=True, blank=True, max_length=20)
    data_assinatura = models.DateTimeField('Data assinatura', null=True, blank=True)
    contrato = models.FileField(upload_to=escola_contrato_path, null=True, blank=True)
    valor = models.DecimalField(
        'valor',
        max_digits=7,
        decimal_places=2)
    nr_parcela = models.PositiveSmallIntegerField('Nr de Parcelas')
    vencimento = models.IntegerField(
        u'Dia de Pagar',
        validators=[validate_vencimento],
    )
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
        ordering = ('aluno__nome',)

    def __str__(self):
        return "Contrato %d:  %s - %s" % (self.ano, self.aluno.nome, self.aluno.escola.nome)

    def set_matricula(self):
        data = date.today()
        Pagamento.objects.get_or_create(titulo='Matrícula %s ' % (self.ano) ,
                                        contrato=self,
                                        escola=self.aluno.escola,
                                        data_prevista=data,
                                        valor=self.matricula_valor,
                                        observacao='',
                                        nr_parcela=None)

    def set_parcelas(self):
        self.set_matricula()
        valor = (self.valor - self.matricula_valor) / self.nr_parcela
        for p in range(1, self.nr_parcela + 1):
            data =  date(self.ano, p, self.vencimento)
            Pagamento.objects.get_or_create(titulo='Parcela %s / %s ' % (p, self.nr_parcela) ,
                                            contrato=self,
                                            escola=self.aluno.escola,
                                            data_prevista=data,
                                            valor=valor,
                                            observacao='',
                                            nr_parcela=p)


class PagamentoManager(models.Manager):
    def get_recebimentos_pendentes(self):
        pass
        """Contratos com recebimentos pendentes de parcelas vencidas"""
        # estagio_valido = ~Q(contrato__estagio__in=[5, 6])
        # pag_lib = Q(pag_lib=1)  # pagamento liberado
        # pag_nao_efetuado = Q(efet=False) | Q(efet=None)
        # query = estagio_valido & pag_lib & pag_nao_efetuado

        # return self.filter(query).order_by('-data_prevista')


class Pagamento(models.Model):
    escola = models.ForeignKey('escolas.Escola')
    titulo = models.CharField(verbose_name=u'Título', max_length=255)
    contrato = models.ForeignKey(ContratoAluno, null=True, blank=True)
    data_prevista = models.DateField(blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    data_pag = models.DateField(blank=True, null=True)
    valor_pag = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    efet = models.BooleanField(blank=True, default=False)
    observacao = models.TextField(verbose_name=u'Observacao')
    tipo = models.SmallIntegerField(u"Tipo", null=True, blank=True) # (+ -)
    parcela = models.ForeignKey( # ID do Pagamento 'Pai'
        'Pagamento',  # SE tem É parcela
        null=True,
        blank=True
    )
    nr_parcela = models.PositiveSmallIntegerField(
        u'Nr de Parcelas',
        null=True,
        blank=True
    )
    nr_documento = models.CharField(verbose_name=u'Nr Documento', max_length=20, null=True, blank=True)
    # categoria = models.ForeignKey(Categoria, null=True, blank=True)
    # cartao = models.ForeignKey(CartaoCredito, null=True, blank=True)


    objects = PagamentoManager()

    class Meta:
        ordering = ('data_prevista',)

    def __str__(self):
        return self.titulo

    def get_valor_com_desconto(self):
        # import pdb; pdb.set_trace()
        #TODO:
        # calcular por dias úteis ou data específica
        time5 = (self.data_prevista - date.today()).days
        if time5 > 5:
            desconto = self.valor * (self.contrato.desconto/ 100)
            return self.valor - desconto
        return self.valor

