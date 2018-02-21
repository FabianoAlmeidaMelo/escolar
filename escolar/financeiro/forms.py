# coding: utf-8
from localbr.formfields import BRDateField, BRDecimalField

from django import forms
from django.db.models import Q
from django.forms.utils import ErrorList
from escolar.financeiro.models import (
    ANO,
    ContratoAluno,
    Pagamento,
    ParametrosContrato,
)

from datetime import date
from calendar import monthrange

months = (list(range(1,13)))
meses = (list(range(1,13)))
meses.insert(0, '--')
months.insert(0, None)
MESES = tuple(zip(months, meses))

hoje = date.today()
ano_corrente = hoje.year
mes_corrnete = hoje.month

PAGAMENTO_STATUS_CHOICES=( 
    (1,'Pago'),
    (0,'Em Aberto'),
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


class ParametrosContratoForm(forms.ModelForm):
    material_parcelas = forms.ChoiceField(label='Nr de Parcelas/ apostilas', choices=PARCELAS_MATERIAL, required=False)
    multa = BRDecimalField(label='Multa por atraso mensalidade (%)', required=False)
    juros = BRDecimalField(label='Juros por atraso mensalidade (%)', required=False)

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
        juros = cleaned_data['juros']
        condicao_juros = cleaned_data['condicao_juros']
        material_parcelas = cleaned_data['material_parcelas']
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
        if condicao_desconto and not tem_desconto:
            errors_list.append("Deve marcar que tem desconto")
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

        for k in data_dict.keys():
            if k <= int(material_parcelas) and data_dict[k] is False:
                errors_list.append("Número de datas abaixo do Nr das parcelas")
            if k > int(material_parcelas) and data_dict[k] is True:
                errors_list.append("Número de datas acima do Nr das parcelas")
        # import pdb; pdb.set_trace()
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
    serie = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.aluno = kwargs.pop('aluno', None)
        super(ContratoAlunoForm, self).__init__(*args, **kwargs)
        self.fields['responsavel'].queryset = self.aluno.membrofamilia_set.filter(responsavel_financeiro=True)
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
        exclude = ('aluno', 'date_add', 'date_upd', 'user_add', 'user_upd') 

    def clean(self):
        cleaned_data = super(ContratoAlunoForm, self).clean()
        material_valor = cleaned_data['material_valor']
        material_parcelas = cleaned_data['material_parcelas']
 
        if any([material_valor, material_parcelas]):
            errors_list = []
            if not material_valor:
                errors_list.append("material_valor")
            if not material_parcelas:
                errors_list.append("material_parcelas")
            for error in errors_list:
                self._errors[error] = ErrorList([u'Campo obrigatório.'])
        
        return cleaned_data

    def save(self, *args, **kwargs):
        if not self.instance.pk:
            self.instance.user_add = self.user
        self.instance.user_upd = self.user
        self.instance.aluno = self.aluno
        instance = super(ContratoAlunoForm, self).save(*args, **kwargs)
        instance.save()
        if instance.pagamento_set.count() == 0:
            instance.set_parcelas()
        return instance


class ContratoAlunoSearchForm(forms.Form):
    '''
    #31
    '''
    responsavel = forms.CharField(label=u'Responsável', required=False)
    aluno = forms.CharField(label=u'Aluno', required=False)
    ano = forms.ChoiceField(label='Ano', choices=ANO, initial=ano_corrente)
    serie = forms.CharField(label=u'Série', required=False)
    curso = forms.CharField(label=u'Curso', required=False)

    def __init__(self, *args, **kargs):
        self.escola = kargs.pop('escola', None)
        super(ContratoAlunoSearchForm, self).__init__(*args, **kargs)
       

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
            if serie:
                q = q & Q(serie__icontains=serie)
            curso = self.cleaned_data['curso']
            if curso:
                q = q & Q(curso__icontains=curso)

        return ContratoAluno.objects.filter(q)


class PagamentoForm(forms.ModelForm):
    tipo = forms.ChoiceField(label="Tipo", choices=TIPO_CHOICES, required=True)
    valor = BRDecimalField(label="Valor", required=True)
    valor_pag = BRDecimalField(label="Valor pago", required=False)
    efet = forms.BooleanField(label="Pago", required=False)
    data_pag = BRDateField(label="Pagamento efetivado em", required=False)
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.escola = kwargs.pop('escola', None)
        self.contrato = kwargs.pop('contrato', None)
        super(PagamentoForm, self).__init__(*args, **kwargs)
        

    class Meta:
        model = Pagamento
        exclude = ('escola', 
                   'contrato',
                   'parcela',
                   'nr_parcela',
                   'date_add',
                   'date_upd',
                   'user_add',
                   'user_upd') 


    def save(self, *args, **kwargs):
        if not self.instance.pk:
            self.instance.user_add = self.user
        self.instance.user_upd = self.user
        self.instance.escola = self.escola
        if self.contrato:
            self.instance.contrato = self.contrato
        instance = super(PagamentoForm, self).save(*args, **kwargs)
        instance.save()
        return instance


class PagamentoEscolaSearchForm(forms.Form):
    '''
    #31
    '''
    efet = forms.ChoiceField(label="Pagamento", choices=PAGAMENTO_STATUS_CHOICES, widget=forms.RadioSelect(), required=False)
    responsavel = forms.CharField(label=u'Responsável', required=False)
    titulo = forms.CharField(label=u'Título', required=False)
    aluno = forms.CharField(label=u'Aluno', required=False)
    ano = forms.ChoiceField(label='Ano', choices=ANO, initial=ano_corrente, required=False)
    mes = forms.ChoiceField(label='Mês', choices=MESES, initial=mes_corrnete, required=False)
    serie = forms.CharField(label=u'Série', required=False)
    curso = forms.CharField(label=u'Curso', required=False)

    def __init__(self, *args, **kargs):
        self.escola = kargs.pop('escola', None)
        super(PagamentoEscolaSearchForm, self).__init__(*args, **kargs)
       

    def get_result_queryset(self, mes=None):
        q = Q(escola=self.escola)
        if self.is_valid():
            # responsavel = self.cleaned_data['responsavel']
            # if responsavel:
            #     q = q & Q(contrato__responsavel__nome__icontains=responsavel)
            # aluno = self.cleaned_data['aluno']
            # if aluno:
            #     q = q & Q(contrato__aluno__nome__icontains=aluno)
            ano = self.cleaned_data['ano']
            if ano:
                q = q & Q(contrato__ano=ano)

            mes = self.cleaned_data['mes']
            if mes and ano:
                year = int(ano)
                month = int(mes)
                data_ini = date(year, month, 1)
                data_fim = date(year, month, monthrange(year, month)[1])
                print('\n FORM:\n',data_ini, data_fim)
                q = q & Q(data_prevista__gte=data_ini, data_prevista__lte=data_fim)

            titulo = self.cleaned_data['titulo']
            if titulo:
                q = q & Q(titulo__icontains=titulo)

            # serie = self.cleaned_data['serie']
            # if serie:
            #     q = q & Q(contrato__serie__icontains=serie)
            # curso = self.cleaned_data['curso']
            # if curso:
            #     q = q & Q(contrato__curso__icontains=curso)

            efet = self.cleaned_data['efet']
            if efet and efet == '1':
                q = q & Q(efet=True)
            if efet and efet == '0':
                q = q & Q(efet=False)
            print(Pagamento.objects.filter(q).count())
        return Pagamento.objects.filter(q)


class PagamentoAlunoEscolaSearchForm(forms.Form):
    '''
    #35
    '''
    efet = forms.ChoiceField(label="Pagamento", choices=PAGAMENTO_STATUS_CHOICES, widget=forms.RadioSelect(), required=False)
    ano = forms.ChoiceField(label='Ano', choices=ANO, initial=ano_corrente, required=False)
    titulo = forms.CharField(label=u'Título', required=False)

    def __init__(self, *args, **kargs):
        self.escola = kargs.pop('escola', None)
        self.aluno = kargs.pop('aluno', None)
        super(PagamentoAlunoEscolaSearchForm, self).__init__(*args, **kargs)
 

    def get_result_queryset(self):
        q = Q(escola=self.escola, contrato__aluno=self.aluno)
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