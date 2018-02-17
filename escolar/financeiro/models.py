# coding: utf-8
from django.apps import apps
from django.db import models
from django.db.models import Q
from escolar.escolas.models import ANO
from escolar.core.models import UserAdd, UserUpd
from datetime import date
from dateutil.relativedelta import relativedelta
from escolar.utils.numextenso import numero_extenso
from datetime import datetime, timedelta, date


ano_corrente = date.today().year
ano_seguinte = ano_corrente + 1
ano_anterior = ano_corrente - 1
 
ANO = (
    (None, '--'),
    (ano_anterior, ano_anterior),
    (ano_corrente, ano_corrente),
    (ano_seguinte, ano_seguinte),
)


def escola_contrato_path(instance, logo):
    '''
    escola que fez o upload do arquivo
    file will be uploaded to MEDIA_ROOT/conta_<id>/<filename>
    '''
    return 'escola_{0}/contratos/{1}'.format(instance.nome, contrato)

def validate_vencimento(value):
    if value not in range(1, 29):
        raise ValidationError(u'%s Não está entre 1 e 28' % value)


CONDICAO_DESCONTO = (
    (None, '--'),
    (1, 'Pagamento até a data vencimento'),
    (2, 'Pagamento até determinado dia útil'),
)

JUROS_EXPECIFICACAO = (
    (None, "--"),
    (1, "Por dia"),
    (2, "Por Mês"),
)

DIA_UTIL = (
    (None, '--'),
    (1, '1º'),
    (2, '2º'),
    (3, '3º'),
    (4, '4º'),
    (5, '5º'),
    (6, '6º'),
    (7, '7º'),
    (8, '8º'),
    (9, '9º'),
    (10, '10º'),
    (11, '11º'),
    (12, '12º'),
)

class ParametrosContrato(models.Model):
    '''
    para Escolas de educação infantil até o 2º grau
    1 desses por escola
    criado no save() de escolas.EscolaForm()
    '''
    ano = models.SmallIntegerField('Ano', choices=ANO) # pelo ano valida as datas
    escola = models.ForeignKey('escolas.Escola')
    tem_desconto = models.BooleanField('tem desconto', default=False)
    condicao_desconto = models.SmallIntegerField('condição desconto', choices=CONDICAO_DESCONTO, null=True, blank=True)
    dia_util =  models.SmallIntegerField('dia útil', choices=DIA_UTIL, null=True, blank=True)
    multa = models.DecimalField('Multa por atraso mensalidade (%)', max_digits=4, decimal_places=2, null=True, blank=True)
    juros = models.DecimalField('Juros por atraso mensalidade (%)', max_digits=4, decimal_places=2, null=True, blank=True)
    condicao_juros = models.SmallIntegerField('condição juros', choices=JUROS_EXPECIFICACAO, null=True, blank=True)
    # no form, limita de 0 a 6, e serve para validar a quantidade de datas das parcelas  
    material_parcelas = models.PositiveSmallIntegerField('Nr de Parcelas/ apostilas', null=True, blank=True)
    data_um_material = models.DateField('1ª parcela em', blank=True, null=True)
    data_dois_material = models.DateField('2ª parcela em', blank=True, null=True)
    data_tres_material = models.DateField('3ª parcela em', blank=True, null=True)
    data_quatro_material = models.DateField('4ª parcela em', blank=True, null=True)
    data_cinco_material = models.DateField('5ª parcela em', blank=True, null=True)
    data_seis_material = models.DateField('6ª parcela em', blank=True, null=True)

    def __str__(self):
        return 'Parâmetros / Escola: %s' % self.escola.nome


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

    def get_valor_extenso(self):
        return numero_extenso(self.valor)

    # def set_parcelas_material(self):
    #     '''
    #     calcula valor e data das parcelas 
    #     das apostilas E
    #     Cria os pagamentos
    #     '''
    #     if all([self.material_parcelas,
    #             self.material_valor,
    #             self.material_data_parcela_um]):

    #         month_range = 12 // self.material_parcelas
    #         valor = self.material_valor / self.material_parcelas
    #         #   jan 1, abr 4, jul 7, out 10
    #         #import pdb; pdb.set_trace()
    #         datas = [self.material_data_parcela_um]
    #         i_list = []
    #         if self.material_parcelas > 1:
    #             for i in list(range(1, month_range + 1)):
    #                 i_list.append(i)
    #                 months = i * month_range
    #                 data = self.material_data_parcela_um + relativedelta(months=months)
    #                 datas.append(data)
    #         datas.sort()
    #         count = 0
    #         for data in datas:
    #             count += 1
    #             Pagamento.objects.get_or_create(titulo='Material %d/ %d' % (count, self.material_parcelas) ,
    #                                             contrato=self,
    #                                             escola=self.aluno.escola,
    #                                             data_prevista=data,
    #                                             valor=valor,
    #                                             observacao='',
    #                                             nr_parcela=None,
    #                                             tipo=2)

    #         print(datas)
        
    def set_parcelas_material(self):
        '''
        calcula valor e data das parcelas 
        das apostilas E
        Cria os pagamentos
        '''
        parametros = ParametrosContrato.objects.get(escola=self.aluno.escola, ano=self.ano)

        dates = [parametros.data_um_material,
                 parametros.data_dois_material,
                 parametros.data_tres_material,
                 parametros.data_quatro_material,
                 parametros.data_cinco_material,
                 parametros.data_seis_material]
        
        datas = [data for data in dates if data]

        month_range = 12 // parametros.material_parcelas
        valor = self.material_valor / parametros.material_parcelas

        datas.sort()
        count = 0
        for data in datas:
            count += 1
            Pagamento.objects.get_or_create(titulo='Material %d/ %d' % (count, parametros.material_parcelas) ,
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
        self.set_parcelas_material()
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
class CategoriaPagamento(models.Model):
    # Categorias default para os Contratos, serve para todas Escolas
    # Prestação de Serviços
    # Matrícula
    escola = models.ForeignKey('escolas.Escola', null=True, blank=True)
    nome = models.CharField('Categoria', max_length=50)

    def __str__(self):
        if self.escola:
            return "%s - %s" % (self.nome, self.escola.nome)
        return self.nome

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
    categoria = models.ForeignKey(CategoriaPagamento, null=True, blank=True)
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

    def get_feriados(self):
        '''
        lista os feriados antes da
        data_prevista
        '''
        Feriado = apps.get_model(app_label='core', model_name='Feriado')
        municipio = self.escola.municipio
        uf = int(str(municipio.id_ibge)[:2])
        inicio = date(self.data_prevista.year, self.data_prevista.month, 1)
        feriados = Feriado.objects.filter(Q(type_code=1) | Q(uf_ibge_code=uf) | Q(municipio=municipio))
        feriados = feriados.filter(date__gte=inicio, date__lte=self.data_prevista).values_list('date', flat=True)
        return feriados

    def get_bizday(self, numero):
        # Retorna o dia útil expecificado;
        # numero ex: 5
        # significa  o 5º dia útil
        feriados = self.get_feriados()
        start, end = date(self.data_prevista.year, self.data_prevista.month, 1), self.data_prevista
        dias_uteis = []
        i = 0
        while len(dias_uteis) < numero:
            data = start + timedelta(days=i)
            if data.weekday() not in [5, 6] and data not in feriados:
                dias_uteis.append(data)
            i += 1
        return dias_uteis[numero - 1]

    def get_valor_com_desconto(self):
        # calcular por dias úteis ou data específica
        # time5 = (self.data_prevista - date.today()).days
        if date.today() <= self.get_bizday(5):
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

