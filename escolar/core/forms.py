# coding: utf-8
from localbr.formfields import BRCPFField
from django import forms
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm as AuthAuthenticationForm
from django.contrib.auth.models import Group
from escolar.core.models import (
    Endereco,
    Perfil,
    User,
    UserGrupos,
)

from municipios.widgets import SelectMunicipioWidget
from escolar.escolas.models import Escola
from localflavor.br.forms import BRZipCodeField

class AuthenticationForm(AuthAuthenticationForm):
    keep_me_logged_in = forms.BooleanField(
                                            label=u'Mantenha-me conectado',
                                            required=False
                                        )

class PerfilSearchForm(forms.Form):
    '''
    #32
    '''
    nome = forms.CharField(label=u'Nome', required=False)
    email = forms.CharField(label=u'email', required=False)
    cpf = BRCPFField(required=False, always_return_formated=True, return_format=u'%s%s%s%s', help_text='Somente números')

    def __init__(self, *args, **kargs):
        self.escola = kargs.pop('escola', None)
        super(PerfilSearchForm, self).__init__(*args, **kargs)

    def set_only_number(self, txt):
        numeros = '0123456789'
        only_numeros = ''
        for c in txt:
            if c in numeros:
                only_numeros += c
        return only_numeros

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        if cpf:
            return self.set_only_number(cpf)
        return
       

    def get_result_queryset(self):
        q = Q()
        if self.is_valid():
            nome = self.cleaned_data['nome']
            if nome:
                q = q & Q(nome__icontains=nome)
            email = self.cleaned_data['email']
            if email:
                q = q & Q(email__icontains=email)
            cpf = self.cleaned_data['cpf']
            if cpf:
                q = q & Q(cpf__icontains=cpf)

        return Perfil.objects.filter(q)


class PerfilForm(forms.ModelForm):
    '''
    TODO
    clean para cpf, SE nascimento form > que 18 anos
    cpf required
    '''
    sexo = forms.ChoiceField(choices=((1, 'Masculino'),(2, 'Feminino'),))
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.escola = kwargs.pop('escola', None)
        super(PerfilForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Perfil
        # fields = ['nome', 'email', 'sexo', 'cpf', 'profissao', 'nascimento']
        exclude = ('endereco', 'escolas', 'user')
     

class EnderecoForm(forms.ModelForm):
    cep = BRZipCodeField(label='CEP', required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.escola = kwargs.pop('escola', None)
        self.perfil = kwargs.pop('perfil', None)
        super(EnderecoForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Endereco
        widgets = {'municipio': SelectMunicipioWidget}
        fields = ['cep', 'logradouro', 'numero', 'complemento', 'bairro', 'municipio']

    def save(self, *args, **kwargs):
        self.instance.perfil = self.perfil
        instance = super(EnderecoForm, self).save(*args, **kwargs)
        instance.save()
        return instance


class GrupoForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', )

class UserForm(forms.ModelForm):
    email = forms.EmailField(label='email', required=True)
    nome = forms.CharField(label='nome', required=True)
    grupo = forms.ModelChoiceField(required=True,
                                   queryset=Group.objects.exclude(name='Admin'))
    escola = forms.ModelChoiceField(required=False,
                                    queryset=Escola.objects.all())
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label=u'Confirmação', widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        exclude = ('date_joined', 'is_active', 'password', 'grupos', 'username')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.escola = kwargs.pop('escola', None)
        super(UserForm, self).__init__(*args, **kwargs)
        grupos = UserGrupos.objects.filter(escola=self.escola, user=self.instance).values_list('grupo__id', flat=True)
        self.fields['grupo'].queryset = Group.objects.exclude(id__in=grupos).exclude(id=5)
        self.auto_edicao = self.instance == self.user
        if not self.user.is_admin():
            self.fields['escola'].widget = forms.HiddenInput()


        if self.auto_edicao and not any([self.user.is_admin()]):
            self.fields['grupo'].widget = forms.HiddenInput()
            self.fields['escola'].widget = forms.HiddenInput()
            self.fields['grupo'].required = False


    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2") 
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords diferentes")
        elif password1 and not password2:
            raise forms.ValidationError("Confirme a senha")
        return password2

    def save(self, commit=False):
        '''
        TODO:
        permitir salvar senha de user SE
        - user for o próprio
        - user for admin
            - nesse caso, enviar email com nova senha, para o user e o responsável pelo aluno (se for o caso)
        '''

        password2 = self.cleaned_data.get("password2", False)
        if password2:
            self.instance.set_password(password2)
        self.instance.save()
        
        return self.instance


class UserSearchForm(forms.Form):
    '''
    #31
    '''
    nome = forms.CharField(label=u'Nome', required=False)
    email = forms.CharField(label=u'email', required=False)

    def __init__(self, *args, **kargs):
        self.escola = kargs.pop('escola', None)
        super(UserSearchForm, self).__init__(*args, **kargs)
       

    def get_result_queryset(self):
        q = Q()
        if self.is_valid():
            nome = self.cleaned_data['nome']
            if nome:
                q = q & Q(nome__icontains=nome)
            email = self.cleaned_data['email']
            if email:
                q = q & Q(email__icontains=email)

        return User.objects.filter(q)