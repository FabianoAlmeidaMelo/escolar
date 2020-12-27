# coding: utf-8
from django import forms
from escolar.sites.models import Conteudo


class ConteudoForm(forms.ModelForm):
    '''
    #10
    '''
    chave = forms.CharField(label='Chave', required=False)
    titulo = forms.CharField(label='Título', required=False)
    texto = forms.CharField(label='Texto', widget=forms.Textarea, required=False)
    foto = forms.ImageField(label='Foto', required=False)
    link = forms.CharField(label='Link', required=False)

    class Meta:
        model = Conteudo
        fields = ['escola', 'chave', 'titulo', 'texto', 'foto', 'link']
 
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.escola = kwargs.pop('escola', None)
        super(ConteudoForm, self).__init__(*args, **kwargs)

        if self.user.is_admin() is False:
            # self.fields['escola'].widget = forms.HiddenInput()
            self.fields['chave'].widget = forms.HiddenInput()
