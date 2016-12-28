# coding: utf-8
from django import forms
from django.contrib.auth.forms import AuthenticationForm as AuthAuthenticationForm
from escolar.core.models import User

class AuthenticationForm(AuthAuthenticationForm):
    keep_me_logged_in = forms.BooleanField(
                                            label=u'Mantenha-me conectado',
                                            required=False
                                        )

class UserForm(forms.ModelForm):
    email = forms.EmailField(label='email', required=True)
    nome = forms.CharField(label='nome', required=True)

    class Meta:
        model = User
        exclude = ('date_joined', 'is_active')
