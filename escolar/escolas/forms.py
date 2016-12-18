# coding: utf-8
from django import forms
from escolar.escolas.models import (
    Escola,
    Grupo,
    )

class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        exclude = ('created_at', )


class GrupoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.escola = kwargs.pop('escola', None)
        super(GrupoForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        instance = super(GrupoForm, self).save(*args, **kwargs)
        instance.escola = self.escola
        instance.save()
        return instance

    class Meta:
        model = Grupo
        exclude = ('name', 'escola',)
