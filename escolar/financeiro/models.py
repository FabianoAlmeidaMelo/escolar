# coding: utf-8
from django.db import models
from escolar.escolas.models import ANO
from escolar.core.models import UserAdd, UserUpd
from datetime import date
from dateutil.relativedelta import relativedelta


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
    desconto = models.DecimalField('Desconto por pontualidade',
        max_digits=7,
        decimal_places=2,
        blank=True,
        null=True)
    matricula_valor = models.DecimalField('Valor Matrícula',
        max_digits=7,
        decimal_places=2)
    material_valor = models.DecimalField('valor material', max_digits=5, decimal_places=2, null=True, blank=True)
    material_parcelas = models.PositiveSmallIntegerField('Nr de Parcelas/ material', null=True, blank=True)
    material_data_parcela_um = models.DateTimeField('Data parcela material', null=True, blank=True)

    class Meta:
        verbose_name = 'contrato'
        verbose_name_plural = 'contratos'
        ordering = ('aluno__nome',)

    def __str__(self):
        return "Contrato %d:  %s - %s" % (self.ano, self.aluno.nome, self.aluno.escola.nome)

    def set_matricula(self):
        data = date.today()
        Pagamento.objects.get_or_create(titulo='Matrícula %s' % (self.ano) ,
                                        contrato=self,
                                        escola=self.aluno.escola,
                                        data_prevista=data,
                                        valor=self.matricula_valor,
                                        observacao='',
                                        nr_parcela=None,
                                        tipo=2)

    def set_parcelas_material(self):
        '''
        calcula valor e data das parcelas 
        das apostilas E
        Cria os pagamentos
        '''
        if all([self.material_parcelas,
                self.material_valor,
                self.material_data_parcela_um]):

            month_range = 12 // self.material_parcelas
            valor = self.material_valor / self.material_parcelas
            #   jan 1, abr 4, jul 7, out 10
            #import pdb; pdb.set_trace()
            datas = [self.material_data_parcela_um]
            i_list = []
            if self.material_parcelas > 1:
                for i in list(range(1, month_range + 1)):
                    i_list.append(i)
                    months = i * month_range
                    data = self.material_data_parcela_um + relativedelta(months=months)
                    datas.append(data)
            datas.sort()
            count = 0
            for data in datas:
                count += 1
                Pagamento.objects.get_or_create(titulo='Material %d/ %d' % (count, self.material_parcelas) ,
                                                contrato=self,
                                                escola=self.aluno.escola,
                                                data_prevista=data,
                                                valor=valor,
                                                observacao='',
                                                nr_parcela=None,
                                                tipo=2)

            print(datas)
        


    def set_parcelas(self):
        self.set_matricula()
        valor = (self.valor - self.matricula_valor) / self.nr_parcela
        for p in range(1, self.nr_parcela + 1):
            data =  date(self.ano, p, self.vencimento)
            Pagamento.objects.get_or_create(titulo='Parcela %s / %s' % (p, self.nr_parcela) ,
                                            contrato=self,
                                            escola=self.aluno.escola,
                                            data_prevista=data,
                                            valor=valor,
                                            observacao='',
                                            nr_parcela=p,
                                            tipo=2)


class PagamentoManager(models.Manager):
    def get_recebimentos_pendentes(self):
        pass
        """Contratos com recebimentos pendentes de parcelas vencidas"""
        # estagio_valido = ~Q(contrato__estagio__in=[5, 6])
        # pag_lib = Q(pag_lib=1)  # pagamento liberado
        # pag_nao_efetuado = Q(efet=False) | Q(efet=None)
        # query = estagio_valido & pag_lib & pag_nao_efetuado

        # return self.filter(query).order_by('-data_prevista')


# TIPO_CHOICES = (
#     (1, u'(+)'),
#     (2, u'(-)'),
# )


class Pagamento(models.Model):
    escola = models.ForeignKey('escolas.Escola')
    titulo = models.CharField(verbose_name=u'Título', max_length=255)
    contrato = models.ForeignKey(ContratoAluno, null=True, blank=True)
    data_prevista = models.DateField(blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    data_pag = models.DateField(blank=True, null=True)
    valor_pag = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    efet = models.BooleanField(blank=True, default=False)
    observacao = models.TextField(verbose_name=u'Observacao', blank=True, null=True)
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

    def get_tipo_display(self):
        tipo = {1: '(+)', 2: '(-)'}
        return tipo[self.tipo]

    def get_color_display(self):
        collor = {1: 'blue', 2: 'red', None: 'black'}
        return collor[self.tipo]

    def get_valor_com_desconto(self):
        # import pdb; pdb.set_trace()
        #TODO:
        # calcular por dias úteis ou data específica
        time5 = (self.data_prevista - date.today()).days
        if time5 > 5:
            desconto = self.valor * (self.contrato.desconto/ 100)
            return self.valor - desconto
        return self.valor

    def get_context_alert(self):
        '''
        ref #35
        Destaca o pagamento com datas previstas ultrapassadas
        '''
        hoje = date.today()
        # import pdb; pdb.set_trace()
        if self.data_prevista <= hoje and self.tipo == 1:
            if self.efet is True:
                return "success"
            elif self.efet is None or self.efet is False:
                return "warning"
        elif self.data_prevista <= hoje and self.tipo == 2:
            if self.efet is True:
                return "success"
            elif self.efet is None or self.efet is False:
                return "danger"
        return ""
