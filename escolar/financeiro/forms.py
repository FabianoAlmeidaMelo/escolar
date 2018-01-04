# coding: utf-8
from django import forms
from django.db.models import Q
from django.forms.utils import ErrorList

from escolar.financeiro.models import (
    ContratoEscola, ANO,
)

from datetime import date

ano_corrente = date.today().year

class ContratoEscolaSearchForm(forms.Form):
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
        super(ContratoEscolaSearchForm, self).__init__(*args, **kargs)
        # responsaveis_list_ids = ContratoEscola.objects.filter(escola=self.escola).values_list('responsavel_id', flat=True)
        # self.fields['responsavel'].queryset = ContratoEscola.objects.filter(responsavel__id__in=responsaveis_list_ids)
        # alunos_list_ids = ContratoEscola.objects.filter(escola=self.escola).values_list('aluno_id', flat=True)
        # self.fields['responsavel'].queryset = ContratoEscola.objects.filter(aluno__id__in=alunos_list_ids)
       

    def get_result_queryset(self):
        q = Q(escola=self.escola)
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

        return ContratoEscola.objects.filter(q)