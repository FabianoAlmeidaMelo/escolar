# coding: utf-8
from django import forms
from escolar.escolas.models import Escola

from escolar.comunicacao.models import(
    MensagemDefault,
    MENSAGEM_CHOICES,
)


class MensagemDefaultForm(forms.ModelForm):
    '''
    #5
    '''
    tipo = forms.ChoiceField(
    	label="Tipo:",
    	choices=MENSAGEM_CHOICES,
    	widget=forms.RadioSelect(),
    	required=True
    )
    titulo = forms.CharField(label='Título da mensagem', required=True)
    cabecalho = forms.CharField(label='Cabeçalho', required=True)
    corpo = forms.CharField(label='Corpo', widget=forms.Textarea, required=True)
    assinatura = forms.CharField(label='Assinatura da mensagem', required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.escola = kwargs.pop('escola', None)
        super(MensagemDefaultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = MensagemDefault
        fields = ['tipo', 'cabecalho', 'titulo', 'corpo', 'assinatura']

    def save(self, *args, **kwargs):
        self.instance.escola = self.escola
        instance = super(MensagemDefaultForm, self).save(*args, **kwargs)
        instance.save()
        return instance
