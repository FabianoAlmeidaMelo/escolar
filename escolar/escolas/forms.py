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

    class Meta:
        model = UserGrupos
        exclude = ('user', 'date_joined', 'escola', 'grupo')
