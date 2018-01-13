# coding: utf-8
from django.conf.urls import include, url

from escolar.core.views import (
    grupos_list,
    grupo_form,
    perfis_list,
    usuarios_list,
    usuario_form,
    )

urlpatterns = [
    # Perfil
    # url(r'^escola/(?P<escola_pk>\d+)/perfil_form/$', perfil_form, name='perfil_form'),
    # url(r'^escola/(?P<escola_pk>\d+)/perfil_form/(?P<pk>\d+)/$',perfil_form, name='perfil_form'),
    url(r'^escola/(?P<escola_pk>\d+)/perfis_list/$', perfis_list, name='perfis_list'),
    # User
    url(r'^escola/(?P<escola_pk>\d+)/usuario_form/$', usuario_form, name='usuario_form'),
    url(r'^escola/(?P<escola_pk>\d+)/usuario_form/(?P<pk>\d+)/$',usuario_form, name='usuario_form'),
    url(r'^escola/(?P<escola_pk>\d+)/usuarios_list/$', usuarios_list, name='usuarios_list'),
    #   # Grupos
    url(r'^administracao/grupo_form/$', grupo_form, name='grupo_form'),
    url(r'^administracao/grupo_form/(?P<grupo_pk>\d+)/$', grupo_form, name='grupo_form'),
    url(r'^administracao/grupos_list/$', grupos_list, name='grupos_list'),
    url(r'^administracao/grupos_list/(?P<escola_pk>\d+)/$', grupos_list, name='grupos_list'),
]
