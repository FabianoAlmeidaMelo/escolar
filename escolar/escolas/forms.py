# coding: utf-8
from django import forms
from escolar.escolas.models import (
    Escola,
    )
from django.contrib.auth.models import Group

class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        exclude = ('created_at', )


class GrupoForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', )