# coding: utf-8
from django.conf.urls import include, url

from escolar.escolas.views import (
    alunos_list,
    escolas_list,
    escola_form,
    grupo_form,
    grupos_list,
    professores_list,
    )

urlpatterns = [
    # Escola
    url(r'^escolas/escola_form/$', escola_form, name='escola_form'),
    url(r'^escolas/escola_form/(?P<pk>\d+)/$',escola_form, name='escola_form'),
    url(r'^escolas/escolas_list/$', escolas_list, name='escolas_list'),
#     # Escola
#     url(r'^escolas/(?P<escola_pk>\d+)/grupo_form/$', grupo_form, name='grupo_form'),
#     url(r'^escolas/(?P<escola_pk>\d+)/grupo_form/(?P<grupo_pk>\d+)/$', grupo_form, name='grupo_form'),
    url(r'^escolas/professores_list/$', professores_list, name='professores_list'),
#     # Grupos
    url(r'^escolas/grupo_form/$', grupo_form, name='grupo_form'),
    url(r'^escolas/grupo_form/(?P<grupo_pk>\d+)/$', grupo_form, name='grupo_form'),
    url(r'^escolas/grupos_list/$', grupos_list, name='grupos_list'),
    #  Alunos
    url(r'^escolas/alunos_list/$', alunos_list, name='alunos_list'),
]
