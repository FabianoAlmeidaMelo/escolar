# coding: utf-8
from calendar import monthrange
from datetime import date
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.apps import apps
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string
from escolar.core.models import UserAdd, UserUpd
from escolar.core.utils import add_email_embed_image
from escolar.escolas.models import ANO
from escolar.settings import DEFAULT_FROM_EMAIL, MEDIA_ROOT
from escolar.utils.numextenso import numero_extenso


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
    ano = models.SmallIntegerField('Ano', choices=ANO) # pelo ano valida as datas
    escola = models.ForeignKey('escolas.Escola')
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
    material_parcelas = models.PositiveSmallIntegerField('Nr de Parcelas/ apostilas', null=True, blank=True)
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
    data_assinatura = models.DateTimeField('Data assinatura', null=True, blank=True)
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
    # fim: comum a qualquer contrato ???
    


class ContratoAluno(Contrato):
    '''
    ref #31
    Contrato faz a ligação:
    Escola + Responsavel pelo Aluno + Aluno
    python manage.py dumpdata financeiro.contratoescola --indent=4
    '''
    # INI  CONTRATOS de prestação de serviços para Alunos:
    tem_desconto = models.BooleanField('tem desconto', default=False)
    condicao_desconto = models.SmallIntegerField('condição desconto', choices=CONDICAO_DESCONTO, null=True, blank=True)
    dia_util =  models.SmallIntegerField('dia útil', choices=DIA_UTIL, null=True, blank=True)
    multa = models.DecimalField('Multa por atraso mensalidade (%)', max_digits=4, decimal_places=2, null=True, blank=True)
    juros = models.DecimalField('Juros por atraso mensalidade (%)', max_digits=4, decimal_places=2, null=True, blank=True)
    condicao_juros = models.SmallIntegerField('condição juros', choices=JUROS_EXPECIFICACAO, null=True, blank=True)

    responsavel = models.ForeignKey('escolas.MembroFamilia')
    aluno = models.ForeignKey('escolas.Aluno', related_name='contrato_aluno')
    serie = models.ForeignKey('escolas.Serie', null=True, blank=True,)
    matricula_nr = models.CharField('Nr da Matrícula', null=True, blank=True, max_length=20)
    desconto = models.DecimalField('Desconto por pontualidade (%)',
        max_digits=7,
        decimal_places=2,
        blank=True,
        null=True)
    matricula_valor = models.DecimalField('Valor Matrícula',
        max_digits=7,
        decimal_places=2)
    material_valor = models.DecimalField('valor material', max_digits=5, decimal_places=2, null=True, blank=True)
    material_parcelas = models.PositiveSmallIntegerField('Nr de Parcelas/ material', null=True, blank=True)

    class Meta:
        verbose_name = 'contrato'
        verbose_name_plural = 'contratos'
        ordering = ('aluno__nome',)

    def __str__(self):
        return "Contrato %d:  %s - %s" % (self.ano, self.aluno.nome, self.aluno.escola.nome)

    def set_matricula(self):
        data = self.data_assinatura or date.today()
        categoria = CategoriaPagamento.objects.get(id=2)  # Matrícula
        Pagamento.objects.get_or_create(titulo='Matrícula %s' % (self.ano) ,
                                        contrato=self,
                                        escola=self.aluno.escola,
                                        data=data,
                                        valor=self.matricula_valor,
                                        observacao='',
                                        nr_parcela=None,
                                        categoria=categoria,
                                        tipo=1)

    def get_valor_extenso(self):
        return numero_extenso(self.valor)

    def get_datas_parcelas_material(self):
        parametros = ParametrosContrato.objects.get(escola=self.aluno.escola, ano=self.ano)

        dates = [parametros.data_um_material,
                 parametros.data_dois_material,
                 parametros.data_tres_material,
                 parametros.data_quatro_material,
                 parametros.data_cinco_material,
                 parametros.data_seis_material]
        
        return [data for data in dates if data]
        

    def set_parcelas_material(self):
        '''
        calcula valor e data das parcelas 
        das apostilas E
        Cria os pagamentos
        '''
        datas = self.get_datas_parcelas_material()

        month_range = 12 // self.material_parcelas
        valor = self.material_valor / self.material_parcelas

        datas.sort()
        categoria = CategoriaPagamento.objects.get(id=9) # Material Didático
        count = 0
        for data in datas:
            count += 1
            Pagamento.objects.get_or_create(titulo='Material %d/ %d' % (count, self.material_parcelas) ,
                                            contrato=self,
                                            escola=self.aluno.escola,
                                            data=data,
                                            valor=valor,
                                            observacao='',
                                            nr_parcela=None,
                                            categoria=categoria,
                                            tipo=1)

        # print(datas)


    def set_parcelas(self):
        '''
        ref #51
        chamado no ContratoAlunoForm().save()
        '''
        if self.pagamento_set.count() == 0:
            self.set_matricula()
            self.set_parcelas_material()
            valor = (self.valor - self.matricula_valor) / self.nr_parcela
            categoria = CategoriaPagamento.objects.get(id=1)  # serviços educacionais
            for p in range(1, self.nr_parcela + 1):
                data =  date(self.ano, p, self.vencimento)
                Pagamento.objects.get_or_create(titulo='Parcela %s / %s' % (p, self.nr_parcela) ,
                                                contrato=self,
                                                escola=self.aluno.escola,
                                                data=data,
                                                valor=valor,
                                                observacao='',
                                                nr_parcela=p,
                                                categoria=categoria,
                                                tipo=1)

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

    class Meta:
        ordering = ('nome',)

class PagamentoManager(models.Manager):
    def get_recebimentos_pendentes(self):
        pass
        """Contratos com recebimentos pendentes de parcelas vencidas"""
        # estagio_valido = ~Q(contrato__estagio__in=[5, 6])
        # pag_lib = Q(pag_lib=1)  # pagamento liberado
        # pag_nao_efetuado = Q(efet=False) | Q(efet=None)
        # query = estagio_valido & pag_lib & pag_nao_efetuado

        # return self.filter(query).order_by('-data')


class Pagamento(models.Model):
    escola = models.ForeignKey('escolas.Escola')
    titulo = models.CharField(verbose_name=u'Título', max_length=255)
    contrato = models.ForeignKey(Contrato, null=True, blank=True)
    data = models.DateField(blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    efet = models.BooleanField(verbose_name='pago:', blank=True, default=False)
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
        ordering = ('data',)

    def __str__(self):
        return self.titulo

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
        # Retorna o dia útil expecificado;
        # numero ex: 5
        # significa  o 5º dia útil
        # numero = self.escola.parametroscontrato_set.last().dia_util
        dias_uteis = []
        if self.contrato:
            # import pdb; pdb.set_trace()
            numero = self.contrato.contratoaluno.dia_util if self.contrato else 0
            feriados = self.get_feriados()
            start, end = date(self.data.year, self.data.month, 1), self.data
            i = 0
            while len(dias_uteis) < numero:
                data = start + timedelta(days=i)
                if data.weekday() not in [5, 6] and data not in feriados:
                    dias_uteis.append(data)
                i += 1
            return dias_uteis[numero - 1]


    def get_valor_a_pagar(self):
        # calcular por dias úteis ou data específica
        # time5 = (self.data - date.today()).days
        if self.categoria and self.categoria.id == 1 and self.contrato and self.contrato.contratoaluno.tem_desconto: # só Prestação de Serviços
            if date.today() <= self.get_bizday():
                desconto = self.valor * (self.contrato.contratoaluno.desconto / 100)
                return self.valor - desconto
            else:
                return self.valor + self.get_multa() + self.get_juros()
        return self.valor

    def get_multa(self):
        if date.today() > self.data:
            multa = self.contrato.contratoaluno.multa / Decimal('100.')
            return round(self.valor * multa, 2)
        return 0

    def get_juros(self):
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
        # import pdb; pdb.set_trace()
        if self.data <= hoje and self.tipo == 1:
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


    def send_email_recibo(self, user=None):
        '''
        #64 envia email com recibo

        Sò pode chegar aqui, se o responsavel.user Tiver email.
      
        '''
        LOGO_SOS = MEDIA_ROOT + '/images/Logo_Colorido_LetraPreta_Horiz.png'
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
            # Imagem anexada embebida no e-mail
            # instância do e-mail, precisa do img_data para ler o logo e
            # colocálo como anexo no e-mail.
            img_data = open(self.escola.logo.path, 'rb').read()
            img_content_id = 'main_image'  # content id para add o logo sos
            add_email_embed_image(email, img_content_id, img_data)
            email.attach_alternative(html_content, 'text/html')
            return email.send()
