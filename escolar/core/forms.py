# coding: utf-8
from django import forms
from django.contrib.auth.forms import AuthenticationForm as AuthAuthenticationForm

class AuthenticationForm(AuthAuthenticationForm):
    keep_me_logged_in = forms.BooleanField(
                                            label=u'Mantenha-me conectado',
                                            required=False
                                        )
