# coding: utf-8
from copy import deepcopy
from decimal import Decimal
from localbr.formfields import BRDateField, BRDecimalField
from django import forms
from django.apps import apps
from django.db.models import Q
from django.forms.utils import ErrorList
from escolar.financeiro.models import (
    ANO,
    FORMA_PGTO,
    Bandeira,
    BandeiraEscolaParametro,
    CategoriaPagamento,
    ContratoAluno,
    InadimplenteDBView,
    Pagamento,
    ParametrosContrato,
)
from escolar.escolas.models import Curso, MembroFamilia, Serie
from escolar.comunicacao.models import MensagemDefault
from escolar.core.widgets import DateTimePicker

from datetime import date
from calendar import monthrange

months = (list(range(1,13)))
meses = (list(range(1,13)))
meses.insert(0, '--')
months.insert(0, None)
MESES = tuple(zip(months, meses))

hoje = date.today()
ANO_CORRENTE = hoje.year
MES_CORRNETE = hoje.month

PAGAMENTO_STATUS_CHOICES=( 
    (1,'Pago'),
    (0,'Em Aberto'),
    (2, 'Previsto'),
)

CONTRATO_STATUS_CHOICES=( 
    (1,'Assinado'),
    (0,'Não Assinado'),
)

TIPO_CHOICES = (
    (1, u'(+)'),
    (2, u'(-)'),
)

PARCELAS_MATERIAL = (
    (None, '--'),
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
)

PARCELAS_MATRICULA = (
    # (None, 'Zero'),
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
)

COM_OU_SEM = (('1', 'Sem forma Pgto',), ('2', 'Todas formas Pgto',))


class ParametrosContratoForm(forms.ModelForm):
    material_parcelas = forms.ChoiceField(label='Nr de Parcelas/ apostilas', choices=PARCELAS_MATERIAL, required=False)
    multa = BRDecimalField(label='Multa por atraso mensalidade (%)', required=False)
    juros = BRDecimalField(label='Juros por atraso mensalidade (%)', required=False)
    data_um_material = forms.DateField(label='Data', required=False, widget=DateTimePicker(options={"format": "DD/MM/YYYY", "pickTime": False}))
    data_dois_material = forms.DateField(label='Data', required=False, widget=DateTimePicker(options={"format": "DD/MM/YYYY", "pickTime": False}))
    data_tres_material = forms.DateField(label='Data', required=False, widget=DateTimePicker(options={"format": "DD/MM/YYYY", "pickTime": False}))
    data_quatro_material = forms.DateField(label='Data', required=False, widget=DateTimePicker(options={"format": "DD/MM/YYYY", "pickTime": False}))
    data_cinco_material = forms.DateField(label='Data', required=False, widget=DateTimePicker(options={"format": "DD/MM/YYYY", "pickTime": False}))
    data_seis_material = forms.DateField(label='Data', required=False, widget=DateTimePicker(options={"format": "DD/MM/YYYY", "pickTime": False}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.escola = kwargs.pop('escola', None)
        super(ParametrosContratoForm, self).__init__(*args, **kwargs)


    class Meta:
        model = ParametrosContrato
        exclude = ('escola',) 

    def clean(self):
        cleaned_data = super(ParametrosContratoForm, self).clean()
        ano = cleaned_data['ano']
        tem_desconto = cleaned_data['tem_desconto']
        desconto = cleaned_data['desconto']
        condicao_desconto = cleaned_data['condicao_desconto']
        dia_util = cleaned_data['dia_util']
        juros = cleaned_data['juros'] or 0
        condicao_juros = cleaned_data['condicao_juros']
        material_parcelas = cleaned_data['material_parcelas'] or 0
        data_um = cleaned_data['data_um_material']
        data_dois = cleaned_data['data_dois_material']
        data_tres = cleaned_data['data_tres_material']
        data_quatro = cleaned_data['data_quatro_material']
        data_cinco = cleaned_data['data_cinco_material']
        data_seis = cleaned_data['data_seis_material']

        data_dict = {1: bool(data_um),
                     2: bool(data_dois),
                     3: bool(data_tres),
                     4: bool(data_quatro),
                     5: bool(data_cinco),
                     6: bool(data_seis)}

        data_list = [data_um, data_dois, data_tres, data_quatro, data_cinco, data_seis]
        ano_list = [data.year for data in data_list if data]

        errors_list = []
        if tem_desconto and not condicao_desconto:
            errors_list.append("Condição do desconto é requerida")
        if tem_desconto and not desconto:
            errors_list.append("Valor do desconto é requerido")
        # if condicao_desconto and not tem_desconto:
        #     errors_list.append("Deve marcar que tem desconto")
        if condicao_desconto == 1 and dia_util: # até a data vencimento
            errors_list.append("Dia útil não é válido para 'Pagamento até a data do vencimento'")
        if dia_util and condicao_desconto != 2: # Pagamento até determinado dia útil
            errors_list.append("Condição de desconto deve ser 'Pagamento até determinado dia útil'")
        if juros and not condicao_juros:
            errors_list.append("Juros ao mês ou ao dia??")
        if condicao_juros and not juros or juros <= 0:
            errors_list.append("A taxa de juros deve ser maior que Zero")
        if material_parcelas and not any([data_um, data_dois, data_tres, data_quatro, data_cinco, data_seis]):
            errors_list.append("Expecifíque as datas das parcelas de apostilas")
        if any([data_um,
                data_dois,
                data_tres,
                data_quatro,
                data_cinco,
                data_seis]) and not material_parcelas:
            errors_list.append("Expecifique o números de parcelas correspondente às datas das parcelas das apostilas")
        if any([data_um,
                data_dois,
                data_tres,
                data_quatro,
                data_cinco,
                data_seis]):
            for k in data_dict.keys():
                if k <= int(material_parcelas) and data_dict[k] is False:
                    errors_list.append("Número de datas abaixo do Nr das parcelas")
                if k > int(material_parcelas) and data_dict[k] is True:
                    errors_list.append("Número de datas acima do Nr das parcelas")

            if ano_list.count(ano) != int(material_parcelas):
                errors_list.append("o Ano das datas, deve ser igual o ano do formulário")

        for error in errors_list:
            self._errors[error] = ErrorList([])

        return cleaned_data

    def save(self, *args, **kwargs):
        self.instance.escola = self.escola
        instance = super(ParametrosContratoForm, self).save(*args, **kwargs)
        instance.save()
        return instance

class ContratoAlunoForm(forms.ModelForm):
    bolsa = forms.DecimalField(label='Bolsa (%)', max_value=100, min_value=0, max_digits=5, decimal_places=2, required=False)
    valor = forms.DecimalField(min_value=0)
    nr_parcela = forms.ChoiceField(label='Nr de Parcelas', choices=MESES, initial=12, required=True)
    data_assinatura = forms.DateField(label='Data da Matrícula', required=False, widget=DateTimePicker(options={"format": "DD/MM/YYYY", "pickTime": False}))
    parcelas = forms.ChoiceField(label='Nr de Parcelas da Matrícula', choices=PARCELAS_MATRICULA, required=False)
    observacao = forms.CharField(label='Motivo da rescisão', required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.aluno = kwargs.pop('aluno', None)
        super(ContratoAlunoForm, self).__init__(*args, **kwargs)
        self.old_instance = deepcopy(self.instance)
        if self.instance.pk:
            self.fields['parcelas'].initial = self.instance.pagamento_set.filter(categoria__id=2).count()
        responsaveis_ids = self.aluno.responsavel_set.filter(responsavel_financeiro=True).values_list('membro_id', flat=True)
        self.fields['responsavel'].queryset = MembroFamilia.objects.filter(id__in=responsaveis_ids)
        self.fields['data_assinatura'].required = True
        self.fields['serie'].required = True
        self.fields['serie'].queryset = Serie.objects.filter(curso=self.aluno.curso)
        self.fields['valor'].label = 'Valor total do contrato'
        if not self.instance.pk:
            escola = self.aluno.escola
            parametros = escola.parametroscontrato_set.last()
            self.fields['ano'].initial = parametros.ano
            self.fields['tem_desconto'].initial = parametros.tem_desconto
            self.fields['desconto'].initial = parametros.desconto
            self.fields['condicao_desconto'].initial = parametros.condicao_desconto
            self.fields['dia_util'].initial = parametros.dia_util
            self.fields['multa'].initial = parametros.multa
            self.fields['juros'].initial = parametros.juros
            self.fields['condicao_juros'].initial = parametros.condicao_juros
            self.fields['nr_parcela'].initial = 12
            self.fields['matricula_valor'].initial = parametros.matricula_valor
            self.fields['material_parcelas'].initial = parametros.material_parcelas
            self.fields['vencimento'].initial = parametros.vencimento


    class Meta:
        model = ContratoAluno
        exclude = ('aluno',
                   'date_add',
                   'date_upd',
                   'user_add',
                   'user_upd') 

    def clean(self):
        cleaned_data = super(ContratoAlunoForm, self).clean()
        material_valor = cleaned_data['material_valor']
        material_parcelas = cleaned_data['material_parcelas']
        rescindido = cleaned_data['rescindido']
        observacao = cleaned_data['observacao']
 
        if any([material_valor, material_parcelas]):
            errors_list = []
            if not material_valor:
                errors_list.append("material_valor")
            if not material_parcelas:
                errors_list.append("material_parcelas")
            for error in errors_list:
                self._errors[error] = ErrorList([u'Campo obrigatório.'])

        if any([rescindido, observacao]):
            errors_list = []
            if not rescindido:
                errors_list.append("rescindido")
            if not observacao:
                errors_list.append("observacao")
            for error in errors_list:
                self._errors[error] = ErrorList([u'Campo obrigatório.'])

        
        return cleaned_data

    def clean_ano(self):
        ano = self.cleaned_data['ano']
        if ContratoAluno.objects.filter(aluno=self.aluno, ano=ano).count() == 0:
            return ano
        elif self.instance.pk and ContratoAluno.objects.filter(aluno=self.aluno, ano=ano).exclude(pk=self.instance.pk).count() == 0:
            return ano
        else:
            raise forms.ValidationError("Esse aluno já tem contrato para esse ano")

    def clean_nr_parcela(self):
        parcelas = self.cleaned_data['nr_parcela']
        if parcelas and 1 <= int(parcelas) <= 12:
            return parcelas
        raise forms.ValidationError("O número de parcelas deve ser de 1 a 12 ")

    def clean_parcelas(self):
        '''
        NR de PARCELAS da MATRÌCULA
        '''
        parcelas = self.cleaned_data['parcelas']
        if parcelas:
            self.instance.parcelas = parcelas
            return self.instance.parcelas

    def save(self, *args, **kwargs):
        if not self.instance.pk:
            self.instance.user_add = self.user
        self.instance.user_upd = self.user
        self.instance.aluno = self.aluno
        if self.old_instance.rescindido != self.instance.rescindido:
            AlunoHistorico = apps.get_model('escolas', 'AlunoHistorico')
            historico = AlunoHistorico()
            historico.aluno = self.aluno
            ato = 'Sim' if self.instance.rescindido else 'Retomado'
            historico.descricao = 'Rescisão: %s do contrato ano %s , obs: ' % (ato, self.instance.ano) 
            historico.descricao += self.instance.observacao or 'Reativado'
            historico.usuario = self.user
            historico.save()
        instance = super(ContratoAlunoForm, self).save(*args, **kwargs)
        instance.save()
        if instance.pagamento_set.filter(efet=True).count() == 0:
            instance.set_parcelas(instance.parcelas)
        return instance


class ContratoAlunoSearchForm(forms.Form):
    '''
    #31
    '''
    responsavel = forms.CharField(label=u'Responsável', required=False)
    aluno = forms.CharField(label=u'Aluno', required=False)
    ano = forms.ChoiceField(label='Ano', choices=ANO, initial=ANO_CORRENTE)
    serie = forms.ModelChoiceField(label=u'Série', queryset=Serie.objects.all(), required=False)
    curso = forms.ModelChoiceField(label=u'Curso', queryset=Curso.objects.all(), required=False)
    assinado = forms.ChoiceField(label="Assinado", choices=CONTRATO_STATUS_CHOICES, widget=forms.RadioSelect(), required=False)

    def __init__(self, *args, **kargs):
        self.escola = kargs.pop('escola', None)
        super(ContratoAlunoSearchForm, self).__init__(*args, **kargs)
        cursos_ids = self.escola.cursos.all().values_list('id', flat=True)
        self.fields['serie'].queryset = Serie.objects.filter(curso__id__in=cursos_ids)
        self.fields['curso'].queryset = self.escola.cursos.all()
       

    def get_result_queryset(self):
        q = Q(aluno__escola=self.escola)
        if self.is_valid():
            responsavel = self.cleaned_data['responsavel']
            if responsavel:
                q = q & Q(responsavel__nome__icontains=responsavel)
            aluno = self.cleaned_data['aluno']
            if aluno:
                q = q & Q(aluno__nome__icontains=aluno)
            ano = self.cleaned_data['ano']
            if ano:
                q = q & Q(ano=ano)

            serie = self.cleaned_data['serie']
            if serie and ano:
                q = q & Q(aluno__ano=int(ano), serie=serie)

            curso = self.cleaned_data['curso']
            if curso and ano:
                q = q & Q(aluno__ano=int(ano), aluno__curso=curso)

            assinado = self.cleaned_data['assinado']
            if assinado and assinado == '1':
                q = q & Q(assinado=True)
            if assinado and assinado == '0':
                q = q & Q(assinado=False)

        return ContratoAluno.objects.filter(q)


class CategoriaPagamentoForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.escola = kwargs.pop('escola', None)
        super(CategoriaPagamentoForm, self).__init__(*args, **kwargs)
        self.can_edit = True

        if self.instance.id and self.instance.pagamento_set.count():
            self.can_edit = False
            self.fields['nome'].widget = forms.HiddenInput()
            self.fields['nome'].required = False

    class Meta:
        model = CategoriaPagamento
        exclude = ('escola', )


    def save(self, *args, **kwargs):
        self.instance.escola = self.escola
        instance = super(CategoriaPagamentoForm, self).save(*args, **kwargs)
        instance.save()
        return instance


class BandeiraForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.escola = kwargs.pop('escola', None)
        super(BandeiraForm, self).__init__(*args, **kwargs)
        self.can_edit = True
        if self.instance.pk and self.instance.pk in [1, 2, 3, 4, 5, 6, 7]:
            self.can_edit = False
            self.escola = None
            self.fields['nome'].widget = forms.HiddenInput()
            self.fields['nome'].required = False

        if self.instance.id and self.instance.pagamento_set.count():
            self.can_edit = False
            self.fields['nome'].widget = forms.HiddenInput()
            self.fields['nome'].required = False

    class Meta:
        model = Bandeira
        exclude = ('escola', )


    def save(self, *args, **kwargs):
        self.instance.escola = self.escola
        instance = super(BandeiraForm, self).save(*args, **kwargs)
        instance.save()
        return instance


class BandeiraEscolaParametroForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        self.bandeira = kwargs.pop('bandeira', None)
        self.escola = kwargs.pop('escola', None)
        super(BandeiraEscolaParametroForm, self).__init__(*args, **kwargs)
        self.can_edit = True

    class Meta:
        model = BandeiraEscolaParametro
        exclude = ('escola', 'bandeira', )


    def save(self, *args, **kwargs):
        self.instance.escola = self.escola
        self.instance.bandeira = self.bandeira
        instance = super(BandeiraEscolaParametroForm, self).save(*args, **kwargs)
        instance.save()
        return instance


class PagamentoForm(forms.ModelForm):
    tipo = forms.ChoiceField(label="Tipo", choices=TIPO_CHOICES, required=True)
    valor = BRDecimalField(label="Valor", required=True)
    # valor_pag = BRDecimalField(label="Valor pago", required=False)
    efet = forms.BooleanField(label="Pago", required=False)
    categoria =forms.ModelChoiceField(queryset=CategoriaPagamento.objects.exclude(id__in=[1, 2, 9]), required=True)
    data = forms.DateField(label='Data', required=True, widget=DateTimePicker(options={"format": "DD/MM/YYYY", "pickTime": False}))
    data_pag = forms.DateField(label="Pagamento efetivado em", widget=DateTimePicker(options={"format": "DD/MM/YYYY", "pickTime": False}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.escola = kwargs.pop('escola', None)
        self.contrato = kwargs.pop('contrato', None)
        super(PagamentoForm, self).__init__(*args, **kwargs)
        self.old_instance = deepcopy(self.instance)

        self.fields['bandeira'].queryset=Bandeira.objects.get_bandeiras_ativas(self.escola)

        if self.contrato:
            self.fields['categoria'].queryset=CategoriaPagamento.objects.filter(id__in=[1, 2, 9])
        if self.instance.pk and self.instance.categoria:
            if self.instance.categoria.id in [1, 2, 9]:
                self.fields['categoria'].widget = forms.HiddenInput()
    

    def clean(self):
        cleaned_data = super(PagamentoForm, self).clean()
        forma_pgto = cleaned_data['forma_pgto']
        bandeira = cleaned_data['bandeira']

        if forma_pgto in [2, 3] and not bandeira:
            raise forms.ValidationError("selecione a Bandeira do Cartão")
        elif bandeira and not forma_pgto:
            raise forms.ValidationError("Selecione a forma de pagamento: Cartão de débito ou Cartão de Crédito")
    
        return cleaned_data

    class Meta:
        model = Pagamento
        exclude = ('escola', 
                   'contrato',
                   'parcela',
                   'nr_parcela',
                   'date_add',
                   'date_upd',
                   'user_add',
                   'user_upd',
                   'taxa_cartao') 


    def save(self, *args, **kwargs):
        if not self.instance.pk:
            self.instance.user_add = self.user
        if self.instance.pk and self.instance.categoria.id in [1, 2]:
            self.instance.titulo = self.old_instance.titulo
        if (self.old_instance.efet is False and
            self.instance.efet is True and not self.instance.data_pag):
            self.instance.data_pag = datetime.today()
        self.instance.user_upd = self.user
        self.instance.escola = self.escola
        if self.contrato:
            self.instance.contrato = self.contrato
        if self.instance.bandeira:
            self.instance.taxa_cartao = self.instance.bandeira.get_taxa(self.escola, self.instance.forma_pgto)
        instance = super(PagamentoForm, self).save(*args, **kwargs)
        instance.save()
        # GUARDA no HISTORICO:
        if self.contrato:
            AlunoHistorico = apps.get_model('escolas', 'AlunoHistorico')
            historico = AlunoHistorico()
            historico.aluno = self.contrato.contratoaluno.aluno
            historico.descricao = 'Pagamento: %s  | ' % self.instance.titulo
            historico.descricao += self.instance.get_alteracao(self.old_instance, instance)
            historico.usuario = self.user
            historico.save()
        return instance


class PagamentoEscolaSearchForm(forms.Form):
    '''
    #31 pagamentos Administração
    '''

    efet = forms.ChoiceField(label="Pagamento", choices=PAGAMENTO_STATUS_CHOICES, widget=forms.RadioSelect(), required=False)
    tipo = forms.ChoiceField(label="Tipo", choices=TIPO_CHOICES, widget=forms.RadioSelect(), required=False)
    titulo = forms.CharField(label=u'Título', required=False)
    ano = forms.ChoiceField(label='Ano', choices=ANO, initial=ANO_CORRENTE, required=False)
    mes = forms.ChoiceField(label='Mês', choices=MESES, initial=MES_CORRNETE, required=False)
    mes_fim = forms.ChoiceField(label='Mês fim', choices=MESES, initial=MES_CORRNETE, required=False)
    categoria = forms.ModelChoiceField(queryset=CategoriaPagamento.objects.all(), required=False)
    serie = forms.ModelChoiceField(label="Série", queryset=Serie.objects.all(), required=False)
    forma_pgto = forms.MultipleChoiceField(
        choices=FORMA_PGTO[1:],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    todas_ou_sem = forms.ChoiceField(widget=forms.RadioSelect, choices=COM_OU_SEM, required=False)
    cpf_resp_fin = forms.CharField(label='CPF resp fin', required=False)

    def __init__(self, *args, **kargs):
        self.escola = kargs.pop('escola', None)
        super(PagamentoEscolaSearchForm, self).__init__(*args, **kargs)

        self.fields['categoria'].queryset = CategoriaPagamento.objects.filter(
            Q(escola=None) |
            Q(escola=self.escola)
        )

        cursos_ids = self.escola.cursos.all().values_list('id', flat=True)

        self.fields['serie'].queryset = Serie.objects.filter(curso_id__in=cursos_ids)
    
    

    def clean(self):
        cleaned_data = super(PagamentoEscolaSearchForm, self).clean()
        ano = cleaned_data['ano']
        mes = cleaned_data['mes']
        mes_fim = cleaned_data['mes_fim']

        if not ano and any([mes, mes_fim]):
            raise forms.ValidationError("Ano é requerido para filtrar por mês")
        elif mes and mes_fim:
            if int(mes_fim) < int(mes):
                raise forms.ValidationError("Mês inicial não pode ser maior que o mês final")

 
        return cleaned_data

    def get_result_queryset(self, mes=None):
        q = Q(escola=self.escola)
        if self.is_valid():
            cpf_resp_fin = self.cleaned_data['cpf_resp_fin']
            if cpf_resp_fin:
                q = q & Q(contrato__contratoaluno__responsavel__cpf__icontains=cpf_resp_fin)
            ano = self.cleaned_data['ano']
            if ano:
                ano = int(ano)
                q = q & Q(data__year=ano)   
            serie = self.cleaned_data['serie']
            if serie:
                q = q & Q(contrato__contratoaluno__serie=serie)

            mes = self.cleaned_data['mes']
            if mes and ano:
                year = int(ano)
                month = mes = int(mes)
                data_ini = date(year, month, 1)
                q = q & Q(data_pag__gte=data_ini)

            mes_fim = self.cleaned_data['mes_fim']
            if mes_fim and ano:
                year = int(ano)
                month =  mes_fim = int(mes_fim)
                data_fim = date(year, month, monthrange(year, month)[1])
                q = q & Q(data_pag__lte=data_fim)

            titulo = self.cleaned_data['titulo']
            if titulo:
                q = q & Q(titulo__icontains=titulo)

            categoria = self.cleaned_data['categoria']
            if categoria:
                q = q & Q(categoria=categoria)

            forma_pgto = self.cleaned_data['forma_pgto']
            if forma_pgto:
                q = q & Q(forma_pgto__in=forma_pgto)

            todas_ou_sem = self.cleaned_data['todas_ou_sem']
            if todas_ou_sem == '2':
                q = q & Q(forma_pgto__in=[1, 2, 3, 4, 5, 6, 7])
            elif todas_ou_sem == '1':
                q = q & Q(forma_pgto=None)

            efet = self.cleaned_data['efet']
            if efet and efet == '1':
                q = q & Q(efet=True)
            if efet and efet == '0':
                q = q & Q(efet=False)
            '''
            se não tem efet 0, 1 ou 2
            E o mês é menor que mes corrente, ou o ano é menor
            que o ano corrente
            o default é 1 pago:
            '''
            # mes_atual = date.today().month
            # if not efet:
            #     if  mes < mes_atual or ano < ANO_CORRENTE:
            #         self.cleaned_data['efet'] = '1'
            #         q = q & Q(efet=True)
            tipo = self.cleaned_data['tipo']
            if tipo and tipo == '1':
                q = q & Q(tipo=1)
            if tipo and tipo == '2':
                q = q & Q(tipo=2)
            return Pagamento.objects.filter(q).exclude(valor=Decimal('0'))
        return Pagamento.objects.filter(q)

ORDER = (
    ("responsavel_nome", "alfabética"),
    ("pagamentos_atrasados", "Menos pgtos atrasados"),
    ("-pagamentos_atrasados", "Mais pgtos atrasados"),
)

class InadimplentesSearchForm(forms.Form):
    '''
    #2 github
    '''
    ano = forms.ChoiceField(label='Ano', choices=ANO[1:], initial=ANO_CORRENTE, required=False)
    serie = forms.ModelChoiceField(label="Série", queryset=Serie.objects.all(), required=False)
    cpf_resp_fin = forms.CharField(label='CPF resp fin', required=False)
    aluno_nome = forms.CharField(label='Aluno Nome', required=False)
    responsavel_nome = forms.CharField(label='resp fin Nome', required=False)
    pagamentos_atrasados = forms.IntegerField(required=False)
    order = forms.ChoiceField(label='Ordenação', choices=ORDER, initial="responsavel_nome", required=False) 

    def __init__(self, *args, **kargs):
        self.escola = kargs.pop('escola', None)
        super(InadimplentesSearchForm, self).__init__(*args, **kargs)

        cursos_ids = self.escola.cursos.all().values_list('id', flat=True)

        self.fields['serie'].queryset = Serie.objects.filter(curso_id__in=cursos_ids)
    
    

    def get_result_queryset(self, mes=None):
        order = "responsavel_nome"
        ano = ANO_CORRENTE
        q = Q(escola=self.escola)
        q = q & Q(ano=ano)
        if self.is_valid():
            order = self.cleaned_data['order']
            cpf_resp_fin = self.cleaned_data['cpf_resp_fin']
            if cpf_resp_fin:
                q = q & Q(cpf_resp_fin__icontains=cpf_resp_fin)
            ano = self.cleaned_data['ano']
            if ano:
                ano = int(ano)
                q = q & Q(ano=ano)   
            serie = self.cleaned_data['serie']
            if serie:
                q = q & Q(serie=serie)
            responsavel_nome = self.cleaned_data['responsavel_nome']
            if responsavel_nome:
                q = q & Q(responsavel_nome__icontains=responsavel_nome)
            aluno_nome = self.cleaned_data['aluno_nome']
            if aluno_nome:
                q = q & Q(aluno_nome__icontains=aluno_nome)
            pagamentos_atrasados = self.cleaned_data['pagamentos_atrasados']
            if pagamentos_atrasados:
                q = q & Q(pagamentos_atrasados=pagamentos_atrasados)

            return InadimplenteDBView.objects.filter(q).exclude(valor=Decimal('0')).order_by(order)
        return InadimplenteDBView.objects.filter(q).order_by(order)



class PagamentoAlunoEscolaSearchForm(forms.Form):
    '''
    #35
    '''
    efet = forms.ChoiceField(label="Pagamento", choices=PAGAMENTO_STATUS_CHOICES, widget=forms.RadioSelect(), required=False)
    ano = forms.ChoiceField(label='Ano', choices=ANO, initial=ANO_CORRENTE, required=False)
    titulo = forms.CharField(label=u'Título', required=False)

    def __init__(self, *args, **kargs):
        self.escola = kargs.pop('escola', None)
        self.aluno = kargs.pop('aluno', None)
        super(PagamentoAlunoEscolaSearchForm, self).__init__(*args, **kargs)
 

    def get_result_queryset(self):
        q = Q(escola=self.escola, contrato__contratoaluno__aluno=self.aluno)
        if self.is_valid():
            ano = self.cleaned_data['ano']
            if ano:
                q = q & Q(contrato__ano=ano)
            
            titulo = self.cleaned_data['titulo']
            if titulo:
                q = q & Q(titulo__icontains=titulo)

            efet = self.cleaned_data['efet']
            if efet and efet == '1':
                q = q & Q(efet=True)
            if efet and efet == '0':
                q = q & Q(efet=False)

        return Pagamento.objects.filter(q)


class EmailMensagemForm(forms.ModelForm):
    '''
    #5
    http://www.proesc.com/blog/escolas-particulares-como-cobrar-mensalidades-atrasadas/
    '''
    email = forms.CharField(label='e-mail', required=True)
    titulo = forms.CharField(label='Título da mensagem', required=True)
    mensagem = forms.CharField(label='Mensagem', widget=forms.Textarea, required=True)
    assinatura = forms.CharField(
        label='Assinatura da mensagem',
        widget=forms.Textarea(attrs={'rows': 6}),
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.escola = kwargs.pop('escola', None)
        super(EmailMensagemForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['titulo'].widget.attrs['readonly'] = True
        self.fields['mensagem'].widget.attrs['readonly'] = True
        self.fields['assinatura'].widget.attrs['readonly'] = True
        
        msg_default = MensagemDefault.objects.get(tipo=1, escola=self.escola)
        valor_divida = self.instance.valor + self.instance.multa + self.instance.juros

        self.fields['titulo'].initial = msg_default.titulo

        modelo = msg_default.cabecalho
        modelo += "\n\n{corpo}".format(corpo=msg_default.corpo)

        modelo = modelo.format(
            data=date.today().strftime("%d/%m/%Y"),
            valor_divida=round(valor_divida, 2),
            nome_completo=self.instance.responsavel_nome,
            pagamentos_atrasados='; '.join(parcela for parcela in self.instance.titulos)
        )

        self.fields['mensagem'].initial = modelo
        self.fields['assinatura'].initial = msg_default.assinatura

    class Meta:
        model = InadimplenteDBView
        fields = ['email',] 
