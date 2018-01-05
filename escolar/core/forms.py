# coding: utf-8
from django import forms
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm as AuthAuthenticationForm
from django.contrib.auth.models import Group
from escolar.core.models import User, UserGrupos
from escolar.escolas.models import Escola

class AuthenticationForm(AuthAuthenticationForm):
    keep_me_logged_in = forms.BooleanField(
                                            label=u'Mantenha-me conectado',
                                            required=False
                                        )

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
        exclude = ('date_joined', 'is_active', 'password', 'grupos')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.escola = kwargs.pop('escola', None)
        super(UserForm, self).__init__(*args, **kwargs)
        grupos = UserGrupos.objects.filter(escola=self.escola, user=self.instance).values_list('grupo__id', flat=True)
        self.fields['grupo'].queryset = Group.objects.exclude(id__in=grupos).exclude(id=5)
        self.auto_edicao = self.instance == self.user
        if not self.user.is_admin():
            self.fields['escola'].widget = forms.HiddenInput()


        if self.auto_edicao and not any([self.user.is_admin(), self.user.is_diretor(self.escola.id)]):
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
        - for criação
        - user for o próprio
        - user for do grupo Diretor
            - nesse caso, enviar email com nova senha, para o user e o responsável pelo aluno (se for o caso)
        '''
        created = False
        email = self.cleaned_data['email']
        group = self.cleaned_data["grupo"] or None
        escola = self.cleaned_data["escola"] or self.escola
        nome = self.cleaned_data['nome']
        if not self.auto_edicao:
            user, created = User.objects.get_or_create(email=email, defaults={'nome': nome})
        else:
            user = self.user

        password2 = self.cleaned_data.get("password2", False)
        if password2 and created or self.auto_edicao:
            self.instance.set_password(password2)
        user.save()
        if all([self.auto_edicao is False, group, escola]):
            user_grupo, grupo_criado = UserGrupos.objects.get_or_create(escola=escola, grupo=group, user=user, ativo=True)
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