# coding: utf-8
from django import forms
from escolar.escolas.models import (
    Escola,
    )
from escolar.core.models import User, UserGrupos


class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        exclude = ('created_at', )


class AlunoForm(forms.ModelForm):
    ativo = forms.BooleanField(label='Matriculado', required=False)

    class Meta:
        model = UserGrupos
        # exclude = ('date_joined', 'escola', 'grupo')
        fields = ('ativo',)

class ProfessorForm(forms.ModelForm):
    ativo = forms.BooleanField(label='Ativo', required=False)

    class Meta:
        model = UserGrupos
        # exclude = ('user', 'date_joined', 'escola', 'grupo')
        fields = ('ativo',)