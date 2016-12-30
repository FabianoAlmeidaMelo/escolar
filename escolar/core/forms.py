# coding: utf-8
from django import forms
from django.contrib.auth.forms import AuthenticationForm as AuthAuthenticationForm
from django.contrib.auth.models import Group
from escolar.core.models import User, UserGrupos
from escolar.escolas.models import Escola

class AuthenticationForm(AuthAuthenticationForm):
    keep_me_logged_in = forms.BooleanField(
                                            label=u'Mantenha-me conectado',
                                            required=False
                                        )

class UserForm(forms.ModelForm):
    email = forms.EmailField(label='email', required=True)
    nome = forms.CharField(label='nome', required=True)
    grupo = forms.ModelChoiceField(required=True,
                                   queryset=Group.objects.exclude(name='Admin'))
    escola = forms.ModelChoiceField(required=False,
                                    queryset=Escola.objects.all())
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label=u'Confirmação', widget=forms.PasswordInput)

    class Meta:
        model = User
        exclude = ('date_joined', 'is_active', 'password', 'grupos')

    # def __init__(self, *args, **kwargs):
    #     super(UserForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords diferentes")
        elif not password2:
            raise forms.ValidationError("Confirme a senha")
        return password2

    def save(self, commit=True):
        email = self.cleaned_data['email']
        nome = self.cleaned_data['nome']
        user, created = User.objects.get_or_create(email=email, defaults={'nome': nome})
        group = self.cleaned_data["grupo"]
        escola = self.cleaned_data["escola"]

        password2 = self.cleaned_data.get("password2", False)
        if password2 and created:
            user.set_password(password2)
        if commit:
            user.save()
        UserGrupos.objects.get_or_create(escola=escola, grupo=group, user=user, ativo=True)
        return user
