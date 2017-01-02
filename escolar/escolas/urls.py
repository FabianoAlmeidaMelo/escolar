# coding: utf-8
from django.conf.urls import include, url

from escolar.escolas.views import (
    alunos_list,
    escolas_list,
    escola_cadastro,
    escola_form,
    professores_list,
    )

urlpatterns = [
    # Escola
    url(r'^escolas/escola_form/$', escola_form, name='escola_form'),
    url(r'^escolas/escola_form/(?P<pk>\d+)/$',escola_form, name='escola_form'),
    url(r'^escolas/escola_cadastro/(?P<pk>\d+)/$',escola_cadastro, name='escola_cadastro'),
    url(r'^escolas/escolas_list/$', escolas_list, name='escolas_list'),
#     # Escola
#     url(r'^escolas/(?P<escola_pk>\d+)/professor_form/$', professor_form, name='professor_form'),
#     url(r'^escolas/(?P<escola_pk>\d+)/professor_form/(?P<grupo_pk>\d+)/$', professor_form, name='professor_form'),
    url(r'^escolas/(?P<escola_pk>\d+)/professores_list/$', professores_list, name='professores_list'),
    #  Alunos
#     url(r'^escolas/(?P<escola_pk>\d+)/aluno_form/$', aluno_form, name='aluno_form'),
#     url(r'^escolas/(?P<escola_pk>\d+)/aluno_form/(?P<grupo_pk>\d+)/$', aluno_form, name='aluno_form'),
    url(r'^escolas/(?P<escola_pk>\d+)/alunos_list/$', alunos_list, name='alunos_list'),
]
