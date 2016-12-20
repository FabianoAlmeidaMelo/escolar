# coding: utf-8
from django import forms
from escolar.escolas.models import (
    Escola,
    )

class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        exclude = ('created_at', )
