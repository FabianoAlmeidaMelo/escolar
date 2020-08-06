# coding: utf-8
from django import forms
from django.forms.utils import ErrorList
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
    assinatura = forms.CharField(
        label='Assinatura da mensagem',
        widget=forms.Textarea(attrs={'rows': 6}),
        required=True
    )


    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.escola = kwargs.pop('escola', None)
        super(MensagemDefaultForm, self).__init__(*args, **kwargs)

        if self.user.is_admin() is False:
            self.fields['tipo'].widget = forms.HiddenInput()

    class Meta:
        model = MensagemDefault
        fields = ['tipo', 'cabecalho', 'titulo', 'corpo', 'assinatura']

    def clean(self):
        errors_list = []
        cleaned_data = super(MensagemDefaultForm, self).clean()

        tipo = int(cleaned_data['tipo'])
        cabecalho = cleaned_data['cabecalho']
        corpo = cleaned_data['corpo']
        if '{data}' not in cabecalho:
            errors_list.append("Não remova o '{data}' do cabeçalho")
        
        if tipo == 1:
            for conteudo in ['{nome_completo}', '{valor_divida}', '{pagamentos_atrasados}']:
                if conteudo not in corpo:
                    errors_list.append("Não remova o '%s' do corpo" % conteudo)

        for error in errors_list:
            self._errors[error] = ErrorList([])


        return cleaned_data


    def save(self, *args, **kwargs):
        self.instance.escola = self.escola
        instance = super(MensagemDefaultForm, self).save(*args, **kwargs)
        instance.save()
        return instance
