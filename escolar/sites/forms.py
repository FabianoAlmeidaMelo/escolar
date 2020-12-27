# coding: utf-8
from django import forms
from escolar.sites.model import Conteudo


class ConteudoForm(forms.ModelForm):
    '''
    #10
    '''
    chave = forms.CharField(label='Chave')
    titulo = forms.CharField(label='Título')
    texto = forms.CharField(label='Texto', widget=forms.Textarea)
    foto = forms.ImageField(label='Foto', required=False)
 