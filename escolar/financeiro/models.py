# coding: utf-8
from calendar import monthrange
from datetime import date
from datetime import datetime, timedelta, date
# import pandas as pd
from decimal import Decimal
from django.forms import ValidationError
from django.apps import apps
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db import models
from django.db.models import DateTimeField, Case, When
from django.db.models import Q
from django.forms.models import model_to_dict
from django.template.loader import render_to_string

from escolar.core.models import UserAdd, UserUpd
from escolar.core.utils import add_email_embed_image

from escolar.escolas.models import ANO

from escolar.settings import DEBUG, DEFAULT_FROM_EMAIL, MEDIA_URL, MEDIA_ROOT
from escolar.utils.numextenso import numero_extenso, extenso
from escolar.comunicacao.models import (
    Mensagem,
    PessoaMensagem,
    MensagemDefault,
)



ano_corrente = date.today().year
ano_seguinte = ano_corrente + 1
ano_anterior = ano_corrente - 1
 
ANO = (
    (None, '--'),
    (ano_anterior, ano_anterior),
    (ano_corrente, ano_corrente),
    (ano_seguinte, ano_seguinte),
)

FORMA_PGTO = (
    (None, '--'),
    (1, 'boleto bancário'),
    (2, 'cartão de crédito'),
    (3, 'cartão de débito'),
    (4, 'cheque'),
    (5, 'dinheiro'),
    (6, 'permuta'),
    (7, 'transferência bancária'),
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
    (1, "pro rata die"),
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
    # ANO corrente e o posterior:
    ano = models.SmallIntegerField('Ano', choices=ANO[2:]) # pelo ano valida as datas
    escola = models.ForeignKey('escolas.Escola', models.CASCADE)
    tem_desconto = models.BooleanField('tem desconto', default=False)
    condicao_desconto = models.SmallIntegerField('condição desconto', choices=CONDICAO_DESCONTO, null=True, blank=True)
    dia_util =  models.SmallIntegerField('dia útil', choices=DIA_UTIL, null=True, blank=True)
    multa = models.DecimalField('Multa por atraso mensalidade (%)', max_digits=4, decimal_places=2, null=True, blank=True)
    juros = models.DecimalField('Juros por atraso mensalidade (%)', max_digits=4, decimal_places=2, null=True, blank=True)
    condicao_juros = models.SmallIntegerField('condição juros', choices=JUROS_EXPECIFICACAO, null=True, blank=True)
    vencimento = models.IntegerField(
        u'Dia de Pagar',
        validators=[validate_vencimento],
    )
    # TODO: desconto irmãos
    # no form, limita de 0 a 6, e serve para validar a quantidade de datas das parcelas  
    material_parcelas = models.PositiveSmallIntegerField('Nr de Parcelas da apostilas', null=True, blank=True)
    data_um_material = models.DateField('1ª parcela em', blank=True, null=True)
    data_dois_material = models.DateField('2ª parcela em', blank=True, null=True)
    data_tres_material = models.DateField('3ª parcela em', blank=True, null=True)
    data_quatro_material = models.DateField('4ª parcela em', blank=True, null=True)
    data_cinco_material = models.DateField('5ª parcela em', blank=True, null=True)
    data_seis_material = models.DateField('6ª parcela em', blank=True, null=True)
    
    # contrato
    desconto = models.DecimalField('Desconto por pontualidade (%)',
        max_digits=7,
        decimal_places=2,
        blank=True,
        null=True)
    matricula_valor = models.DecimalField('Valor Matrícula',
        max_digits=7,
        decimal_places=2)


    def __str__(self):
        return 'Parâmetros / Escola: %s' % self.escola.nome



class Contrato(UserAdd, UserUpd):
    '''
    ContratoAluno herda de Contrato
    '''
    # INI: comum a qualquer contrato ???
    ano = models.SmallIntegerField()
    data_assinatura = models.DateTimeField('Data da Matrícula', null=True, blank=True)
    assinado = models.BooleanField('Assinado', default=False)
    valor = models.DecimalField(
        'valor',
        max_digits=7,
        decimal_places=2)
    nr_parcela = models.PositiveSmallIntegerField('Nr de Parcelas')
    arquivo = models.FileField(upload_to=escola_contrato_path, null=True, blank=True)
    vencimento = models.IntegerField(
        u'Dia de Pagar',
        validators=[validate_vencimento],
        null=True, blank=True)
    rescindido = models.BooleanField(default=False)
    observacao = models.CharField('Observação', max_length=300, null=True, blank=True)
    

class ContratoAluno(Contrato):
    '''
    ref #31
    Contrato faz a ligação:
    Escola + Responsavel pelo Aluno + Aluno
    python manage.py dumpdata financeiro.contratoescola --indent=4
    '''
    # INI  CONTRATOS de prestação de serviços para Alunos:
    bolsa = models.DecimalField('Bolsa (%)',
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True)
    tem_desconto = models.BooleanField('tem desconto', default=False)
    condicao_desconto = models.SmallIntegerField('condição desconto', choices=CONDICAO_DESCONTO, null=True, blank=True)
    dia_util =  models.SmallIntegerField('dia útil', choices=DIA_UTIL, null=True, blank=True)
    multa = models.DecimalField('Multa por atraso mensalidade (%)', max_digits=4, decimal_places=2, null=True, blank=True)
    juros = models.DecimalField('Juros por atraso mensalidade (%)', max_digits=4, decimal_places=2, null=True, blank=True)
    condicao_juros = models.SmallIntegerField('condição juros', choices=JUROS_EXPECIFICACAO, null=True, blank=True)

    responsavel = models.ForeignKey('escolas.MembroFamilia', models.CASCADE)
    aluno = models.ForeignKey('escolas.Aluno', models.CASCADE, related_name='contrato_aluno')
    serie = models.ForeignKey('escolas.Serie', models.SET_NULL, null=True, blank=True,)
    matricula_nr = models.CharField('Nr da Matrícula', null=True, blank=True, max_length=20)
    desconto = models.DecimalField('Desconto por pontualidade (%)',
        max_digits=7,
        decimal_places=2,
        blank=True,
        null=True)
    matricula_valor = models.DecimalField('Valor Matrícula',
        max_digits=7,
        decimal_places=2)
    material_valor = models.DecimalField('valor total das apostilas', max_digits=5, decimal_places=2, null=True, blank=True)
    material_parcelas = models.PositiveSmallIntegerField('Nr de Parcelas da apostila', null=True, blank=True)

    class Meta:
        verbose_name = 'contrato'
        verbose_name_plural = 'contratos'
        ordering = ('aluno__nome',)

    def __str__(self):
        return "Contrato %d: %s - %s" % (self.ano, self.aluno.nome, self.aluno.escola.nome)

    def recalcula_parcelas(self):
        '''
        Verifica se o valor médio das parcelas
        não pagas, está de acordo com o valor
        previsto:
        contrato valor 12000, 12 parcelas de 1000
        contrato valoe 12000 matrícula 600, 12 parcelas de 1000 1 de 600
        Não envolve as Apostilas
        '''
        valor_bolsa = 0
        if self.bolsa:
            valor_bolsa = self.valor  * (self.bolsa / Decimal('100'))

        valor_medio = (self.valor - self.matricula_valor - valor_bolsa) / self.nr_parcela

        self.pagamento_set.filter(efet=False, categoria_id=1).update(valor=valor_medio)



    def parcelas_anuidade(self):
        '''
        (na impressão do contrato)
        para evitar alteração do valor das parcelas,
        por jurus e multas por atraso
        '''
        return self.valor / self.nr_parcela

    def _date_list(self, nr_parcelas, matricula=False):
        '''
        Controla a data das parcelas do: Contrato
        e da Matrícula
        lista um nr de datas = nr parcelas
        no mesmo ano com Base no Ano do contrato

        '''
        data_base = self.data_assinatura.date()
        if self.data_assinatura.year < self.ano and matricula is False:
            data_base = date(self.ano, 1, self.vencimento)

        # sequencia = pd.date_range(start=data_base, periods=nr_parcelas, freq='M')

        datas = [data_base or datetime.today()]

        for seq in sequencia[1:]:
            data = date(seq.year, seq.month, self.vencimento) 
            datas.append(data) 

        return datas

    def date_list(self, nr_parcelas, matricula=False):
        '''
        Controla a data das parcelas do: Contrato
        e da Matrícula
        lista um nr de datas = nr parcelas
        no mesmo ano com Base no Ano do contrato

        '''
        sequencia = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 1, 14: 2,  15: 3,  16: 4,  17: 5,  18: 6, 19: 7, 20: 8, 21: 9, 22: 10, 23: 11, 24: 12}

        data_base = self.data_assinatura.date()
        if self.data_assinatura.year < self.ano and matricula is False:
            data_base = date(self.ano, 1, self.vencimento)

        datas = [data_base or datetime.today()]

        ref = data_base.month
        for i in list(range(1, nr_parcelas)):
            ref += 1
            if ref <= 12:
                data = date(data_base.year, ref, self.vencimento)
            elif ref > 12 and ref <= 24:
                data = date(data_base.year +1, sequencia[ref], self.vencimento)
            else:
                data = date(data_base.year +2, sequencia[ref], self.vencimento)
            datas.append(data) 

        return datas


    def set_matricula(self, nr_parcelas):
        nr_parcelas = int(nr_parcelas)
        if self.matricula_valor and self.matricula_valor > 0:
            valor = self.matricula_valor
            if nr_parcelas > 1:
                valor = self.matricula_valor / nr_parcelas
            datas = self.date_list(nr_parcelas, True)
            nr_parcela = 0
            for data in datas:
                if nr_parcelas > 1:
                    nr_parcela += 1
                else:
                    nr_parcela = None
                categoria = CategoriaPagamento.objects.get(id=2)  # Matrícula
                Pagamento.objects.update_or_create(
                    titulo='Matrícula %s' % (self.ano) ,
                    contrato=self,
                    escola=self.aluno.escola,
                    data=data,
                    data_pag=data,
                    observacao='',
                    nr_parcela=nr_parcela,
                    categoria=categoria,
                    tipo=1,
                    defaults={'valor': valor}
                )

    def get_resp(self):
        return self.responsavel.responsavel_set.filter(
            aluno=self.aluno
        ).first()

    def get_valor_extenso(self):
        return numero_extenso(self.valor)

    def get_descconto_extenso(self):
        return extenso(self.desconto)

    def get_datas_parcelas_material(self):
        if not self.pagamento_set.filter(categoria_id=9, tipo=1).exists():
            parametros = ParametrosContrato.objects.filter(
                escola=self.aluno.escola,
                ano=self.ano
            ).last()
            if parametros:
                dates = [parametros.data_um_material,
                         parametros.data_dois_material,
                         parametros.data_tres_material,
                         parametros.data_quatro_material,
                         parametros.data_cinco_material,
                         parametros.data_seis_material]
            else:
                dates = self.date_list(self.material_parcelas)
        else:
            dates = []
    
        return [data for data in dates if data]
        

    def set_parcelas_material(self):
        '''
        calcula valor e data das parcelas 
        das apostilas E
        Cria os pagamentos
        '''
        if self.material_valor and self.material_valor > 0:
            datas = self.get_datas_parcelas_material()
            nr_parcelas = self.material_parcelas or 1

            valor = self.material_valor / nr_parcelas

            datas.sort()
            categoria = CategoriaPagamento.objects.get(id=9) # Material Didático
            count = 0
            for data in datas:
                count += 1
                Pagamento.objects.update_or_create(
                    titulo='Material %d/ %d' % (count, self.material_parcelas) ,
                    data=data,
                    data_pag=data,
                    contrato=self,
                    escola=self.aluno.escola,
                    categoria=categoria,
                    observacao='',
                    nr_parcela=None,
                    tipo=1, defaults={'valor':valor})


    def set_parcelas(self, parcelas_matricula):
        '''
        ref #51
        chamado no ContratoAlunoForm().save()
        O valor total do contrato, inclui o valor da Matrícula
        que é um adiantamento da anuidade e
        é descontado das parcelas
        '''
        if self.pagamento_set.filter(efet=True).count() == 0:
            self.pagamento_set.all().delete()
            self.set_matricula(parcelas_matricula)
            self.set_parcelas_material()
            valor_bolsa = 0
            if self.bolsa:
                valor_bolsa = self.valor  * (self.bolsa / Decimal('100'))
            if valor_bolsa < self.valor:
                valor = (self.valor - self.matricula_valor - valor_bolsa) / self.nr_parcela
                categoria = CategoriaPagamento.objects.get(id=1)  # serviços educacionais
                mes_ini = 13 - self.nr_parcela  # ex: 10 parcelas, vai começar em março
                n = 1
                for p in range(mes_ini, 12 + 1):
                    data =  date(self.ano, p, self.vencimento)
                    Pagamento.objects.update_or_create(
                        titulo='Parcela %s / %s' % (n, self.nr_parcela) ,
                        contrato=self,
                        escola=self.aluno.escola,
                        data=data,
                        data_pag=data,
                        observacao='',
                        nr_parcela=p,
                        categoria=categoria,
                        tipo=1, 
                        defaults={'valor': valor,})
                    n += 1


class CategoriaPagamento(models.Model):
    # Categorias default para os Contratos, serve para todas Escolas
    # Prestação de Serviços
    # Matrícula
    escola = models.ForeignKey('escolas.Escola', models.CASCADE, null=True, blank=True)
    nome = models.CharField('Categoria', max_length=50)
    descricao = models.CharField('Descrição', max_length=150)

    def __str__(self):
        if self.escola:
            return "%s - %s" % (self.nome, self.escola.nome)
        return self.nome

    class Meta:
        ordering = ('nome',)


class BandeiraManager(models.Manager):

    def get_bandeiras_ativas(self, escola):
        """
        """
        bandeiras_ids = BandeiraEscolaParametro.objects.filter(
            escola=escola,
            ativa=True
        ).values_list('bandeira__id', flat=True)
        return self.filter(id__in=bandeiras_ids)


class Bandeira(models.Model):
    """
    Bandeira de cartões que as Escolas aceitam
    para recebimentos
    """
    nome = models.CharField('Nome', max_length=20, null=False)
    escola = models.ForeignKey('escolas.Escola', models.CASCADE, null=True)

    objects = BandeiraManager()

    class Meta:
        ordering = ('nome',)

    def __str__(self):
        str_obj = '%s' % self.nome
        escola = self.escola
        if escola:
            str_obj = '%s - %s' % (self.escola, self.nome,)
        return str_obj

    def get_taxa(self, escola, meio_pgto):
        if meio_pgto == 2:
            return self.bandeiraescolaparametro_set.filter(
                escola_id=1
            ).first().taxa_credito
        elif meio_pgto == 3:
            return self.bandeiraescolaparametro_set.filter(
                escola_id=1
            ).first().taxa_debito
        else:
            return 0



class BandeiraEscolaParametro(models.Model):
    """
    parâmetros de cada Bandeira de Cartão, por escola
    as bandeiras ativas, ficam disponíveis no cadastro dos
    pagamentos
    """
    bandeira = models.ForeignKey(Bandeira, models.CASCADE)
    escola = models.ForeignKey('escolas.Escola', models.CASCADE)
    ativa = models.BooleanField(default=True)
    taxa_debito = models.DecimalField('Taxa no débto', max_digits=5, decimal_places=2, default=Decimal('0'))
    taxa_credito = models.DecimalField('Taxa no crédito', max_digits=5, decimal_places=2, default=Decimal('0'))
    dias_debito = models.SmallIntegerField('Dia(s) para receber no débto', null=True, blank=True)
    dias_credito = models.SmallIntegerField('Dia(s) para receber no crédito', null=True, blank=True)

    class Meta:
        verbose_name = 'Bandeira Paraâmetros'
        verbose_name_plural = 'Bandeiras Paraâmetros'
        unique_together = ("escola", "bandeira")

    def __str__(self):
        str_obj = '%s - %s' % (self.bandeira.nome, self.taxa_debito)
        escola = self.escola
        if escola:
            str_obj = '%s - %s - %s' % (self.escola.nome, self.bandeira.nome, self.taxa_debito)
        return str_obj


class PagamentoManager(models.Manager):
    # def get_recebimentos_pendentes(self):
    #     pass
    #     """Contratos com recebimentos pendentes de parcelas vencidas"""
    #     estagio_valido = ~Q(contrato__estagio__in=[5, 6])
    #     pag_lib = Q(pag_lib=1)  # pagamento liberado
    #     pag_nao_efetuado = Q(efet=False) | Q(efet=None)
    #     query = estagio_valido & pag_lib & pag_nao_efetuado

    #     return self.filter(query).order_by('-data')

    def get_pontualidade_pagamentos(self, aluno):
        """
        pagamentos.values('data', 'contrato__vencimento', 'contrato__ano')
        """
        return list(self.filter(contrato__contratoaluno__aluno=aluno,
                                categoria__id=1).values('data', 'contrato__vencimento', 'contrato__ano').order_by('data'))


class Pagamento(models.Model):
    escola = models.ForeignKey('escolas.Escola', models.CASCADE)
    titulo = models.CharField(verbose_name=u'Título', max_length=255)
    contrato = models.ForeignKey(Contrato, models.SET_NULL, null=True, blank=True)
    data = models.DateField("data prevista:", blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    data_pag = models.DateTimeField("data pago:", blank=True, null=True)
    efet = models.BooleanField(verbose_name='pago:', blank=True, default=False)
    observacao = models.TextField(verbose_name=u'Observacao', blank=True, null=True)
    tipo = models.SmallIntegerField(u"Tipo", null=True, blank=True) # (+ -)
    parcela = models.ForeignKey( # ID do Pagamento 'Pai'
        'Pagamento',  # SE tem É parcela
        models.SET_NULL,
        null=True,
        blank=True
    )
    nr_parcela = models.PositiveSmallIntegerField(
        u'Nr de Parcelas',
        null=True,
        blank=True
    )
    nr_documento = models.CharField(verbose_name=u'Nr Documento', max_length=20, null=True, blank=True)
    categoria = models.ForeignKey(
        CategoriaPagamento,
        models.SET_NULL,
        null=True, blank=True)
    forma_pgto = models.SmallIntegerField('Forma de pagamento', choices=FORMA_PGTO, null=True, blank=True)
    # cartao = models.ForeignKey(CartaoCredito, null=True, blank=True)
    bandeira = models.ForeignKey(Bandeira, models.SET_NULL, null=True, blank=True)
    # taxa que a bandeira do cartão cobra da escola:
    taxa_cartao = models.DecimalField('Taxa do cartão', max_digits=5, decimal_places=2, default=Decimal('0'))
    bandeira = models.ForeignKey(Bandeira, models.SET_NULL, null=True, blank=True)

    objects = PagamentoManager()

    class Meta:
        ordering = ('data_pag',)

    def __str__(self):
        return self.titulo

    def get_valor_liquido(self):
        '''
        SE tem taxa > 0
        retorna o valor descontado a taxa
        - listagem que vai para o contator XLS
        '''
        valor = self.valor
        if self.taxa_cartao and self.efet:
            tx = self.taxa_cartao / Decimal('100.0')
            valor = self.valor - (tx * self.valor)
        return valor


    def get_valor_extenso(self):
        return numero_extenso(self.valor)

    def get_tipo_display(self):
        tipo = {1: '(+)', 2: '(-)'}
        return tipo[self.tipo]

    def get_color_display(self):
        collor = {1: 'blue', 2: 'red', None: 'black'}
        return collor[self.tipo]

    def get_feriados(self):
        '''
        lista os feriados antes da
        data
        '''
        Feriado = apps.get_model(app_label='core', model_name='Feriado')
        municipio = self.escola.municipio
        uf = int(str(municipio.id_ibge)[:2])
        inicio = date(self.data.year, self.data.month, 1)
        feriados = Feriado.objects.filter(Q(type_code=1) | Q(uf_ibge_code=uf) | Q(municipio=municipio))
        feriados = feriados.filter(date__gte=inicio, date__lte=self.data).values_list('date', flat=True)
        return feriados

    def get_bizday(self):
        """
        Retorna o dia útil expecificado;
        numero ex: 5
        significa  o 5º dia útil
        numero = self.escola.parametroscontrato_set.last().dia_util
        """
        dias_uteis = []
        if self.contrato and self.contrato.contratoaluno.dia_util:
            numero = self.contrato.contratoaluno.dia_util if self.contrato.contratoaluno.dia_util else 1
            feriados = self.get_feriados()
            start, end = date(self.data.year, self.data.month, 1), self.data
            i = 0
            while len(dias_uteis) < numero:
                data = start + timedelta(days=i)
                if data.weekday() not in [5, 6] and data not in feriados:
                    dias_uteis.append(data)
                i += 1
            return dias_uteis[numero - 1]
        else:  # a data prevista do pagamento
            return self.data

    def get_valor_a_pagar(self):
        """
        calcular por dias úteis ou data específica
        time5 = (self.data - date.today()).days
        """
        if self.contrato and not self.contrato.contratoaluno.rescindido and self.efet is False:
            if self.categoria and self.categoria.id == 1 and self.contrato.contratoaluno.desconto or self.contrato.contratoaluno.bolsa: # só Prestação de Serviços
                if date.today() <= self.get_bizday():
                    desconto = self.valor * (self.contrato.contratoaluno.desconto / 100)
                    return self.valor - desconto
                else:
                    return self.valor + self.get_multa() + self.get_juros()
        return self.valor

    def get_multa(self):
        if self.contrato and self.contrato.contratoaluno:
            if all([self.categoria,
                    self.categoria.id == 1,
                    self.contrato, 
                    self.contrato.contratoaluno.juros,
                     date.today() > self.data]):
                multa = self.contrato.contratoaluno.multa / Decimal('100.')
                return round(self.valor * multa, 2)
        return 0

    def get_juros(self):
        if self.contrato and self.contrato.contratoaluno:
            if all([self.categoria,
                    self.categoria.id == 1,
                    self.contrato, 
                    self.contrato.contratoaluno.juros,
                     date.today() > self.data]):
                nr, nr_dias = monthrange(ano_corrente, self.data.month)
                juros_mensal = self.contrato.contratoaluno.juros
                juros_por_dia = juros_mensal / nr_dias
                dias_atrasado = (date.today() - self.data).days
                return round(self.valor * (juros_por_dia * dias_atrasado / 100), 2)
        return 0

    def get_context_alert(self):
        '''
        ref #35
        Destaca o pagamento com datas previstas ultrapassadas
        '''
        hoje = date.today()
        if self.efet:
            return "success"
        elif self.data <= hoje and self.tipo == 1:
            if self.efet is True:
                return "success"
            elif self.efet is None or self.efet is False:
                return "warning"
        elif self.data <= hoje and self.tipo == 2:
            if self.efet is True:
                return "success"
            elif self.efet is None or self.efet is False:
                return "danger"
        return ""


    def get_alteracao(self, old_instance, instance):
        '''
        ref #69
        '''
        dados_alterados = []
        anterior_dict = model_to_dict(old_instance)
        atual_dict = model_to_dict(instance)

        dados_alterados = []
        if anterior_dict != atual_dict:
            for i in atual_dict.items():
                if i not in anterior_dict.items():
                    dados_alterados.append(str(i[0]))
                    dados_alterados.append(' = ')
                    dados_alterados.append(str(i[1]))
                    dados_alterados.append('; ')

        return ' '.join(dados_alterados)


    def send_email_recibo(self, user=None):
        '''
        #64 envia email com recibo

        Sò pode chegar aqui, se o responsavel.user Tiver email.
      
        '''
        LOGO_ESCOLA = ''
        # if DEBUG:
        #     LOGO_ESCOLA = '%s/%s' % (MEDIA_ROOT, self.escola.logo.name)
        # else:
        #     LOGO_ESCOLA = '%s/%s' %  (MEDIA_URL[:-1], self.escola.logo.name)

        emails = [self.contrato.contratoaluno.responsavel.email]
        if emails and self.efet:
            url = ''
            # context (body) vars
            context = {}
            context['escola'] = self.escola
            context['contrato'] = self.contrato.contratoaluno
            context['url'] = url
            context['pagamento'] = self
            context['data'] = date.today()
            context['user'] = user
            # context['usuario'] = user
            
            # conteúdo txt:
            template = 'financeiro/email_recibo.txt'
            text_content = render_to_string(template, context)
            # conteúdo html:
            html_template = 'financeiro/email_recibo.html'
            html_content = render_to_string(html_template, context)
            # email instance:
            assunto = u'Recibo de pagamento/ %s ' % self.escola
            email_kwargs = {}
            email_kwargs['subject'] = assunto
            email_kwargs['body'] = text_content
            email_kwargs['from_email'] = DEFAULT_FROM_EMAIL
            email_kwargs['to'] = emails
            email = EmailMultiAlternatives(**email_kwargs)
            # Imagem anexada embedada no e-mail
            # instância do e-mail, precisa do img_data para ler o logo e
            # colocá-lo como anexo no e-mail.
            # img_data = open(LOGO_ESCOLA, 'rb').read()
            # img_content_id = 'main_image'  # content id para add o logo sos
            # add_email_embed_image(email, img_content_id, img_data)
            email.attach_alternative(html_content, 'text/html')
            return email.send()

    def gerar_complementar(self, previsto, data, valor, obs):
        '''
        Uma parcela foi paga parcialmente e o user quiz grar uma
        outra parcela para complementa-la
        '''
        pagamento = self
        pagamento.id = None
        pagamento.titulo = self.titulo + ': Complementar'
        pagamento.efet = False
        pagamento.observacao = obs
        pagamento.valor = valor
        pagamento.data = data
        pagamento.data_pag = data
        pagamento.save()


class InadimplenteDBView(models.Model):
    ano = models.SmallIntegerField()
    escola = models.ForeignKey('escolas.Escola', models.CASCADE)
    contrato = models.ForeignKey(Contrato, models.CASCADE)
    serie = models.ForeignKey('escolas.Serie', models.CASCADE)
    pagamentos_atrasados = models.SmallIntegerField()
    titulos = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    valor = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))
    multa = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))
    juros = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))
    cpf_resp_fin = models.CharField(max_length=11)
    responsavel_nome = models.CharField(max_length=100)
    celular = models.CharField(max_length=11, null=True, blank=True)
    email = models.EmailField('e-mail', null=True, blank=True)
    aluno_nome = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'view_inadimplentes'


    def send_email_cobranca(self, mensagem):
        '''
        ref #5
        Enviar uma msg de email para o responsável financeiro
        cobrando
        Os meses em atraso
        '''

        emails = [self.email]
        if emails:
            tipo_cobranca = 1
            msg_default = MensagemDefault.objects.filter(
               escola=self.escola,
               tipo=tipo_cobranca
            ).first()
            send_mail(
                msg_default.titulo,
                mensagem,
                settings.DEFAULT_FROM_EMAIL,
                emails,
                fail_silently=False
            )
            return True
        return False

    def get_whats_app_link_cobranca(self):
        link = None
        if self.celular and len(self.celular) >= 10:

            link = "https://api.whatsapp.com/send?phone=55{cel}".format(
                cel=self.celular,
            )
        return link


    def set_mensagem_cobranca(self, mensagem, user):
        '''
        #5 chamado na views: 'cobranca_form'
        Registra a msg enviada e para quem
        '''
        tipo_cobranca = 1
        meio_email = 1
        mensagem = Mensagem.objects.create(
            escola=self.escola,
            data=date.today(),
            user=user,
            texto=mensagem,
            tipo=tipo_cobranca,
            meio=meio_email,
        )
        pessoa_mensagem = PessoaMensagem.objects.create(
            mensagem=mensagem,
            contrato_id=self.contrato.id,
            email=self.email,
            pessoa=self.contrato.contratoaluno.responsavel.pessoa_ptr 
        )

    def get_data_ultima_cobranca(self):
        data = None
        cobranca = PessoaMensagem.objects.filter(
            mensagem__escola=self.escola,
            contrato_id=self.contrato.id
        ).order_by('mensagem__data').last()
        if cobranca:
            data = cobranca.mensagem.data
        return data
