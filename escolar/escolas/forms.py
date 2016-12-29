# coding: utf-8
from django import forms
from escolar.escolas.models import (
    Escola,
    )

from django.contrib.auth.models import Group
from escolar.core.models import User

class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        exclude = ('created_at', )


class GrupoForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', )


class AlunoForm(forms.ModelForm):
    email = forms.EmailField(label='email', required=True)
    nome = forms.CharField(label='nome', required=True)

    class Meta:
        model = User
        exclude = ('date_joined', 'is_active')
