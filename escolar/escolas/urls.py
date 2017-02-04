# coding: utf-8
from django.conf.urls import url

from escolar.escolas.views import (
    aluno_form,
    alunos_list,
    classes_list,
    classe_form,
    escolas_list,
    escola_cadastro,
    escola_form,
    professores_list,
    professor_form,
    )

urlpatterns = [
    # Escola
    url(r'^escola/escola_form/$', escola_form, name='escola_form'),
    url(r'^escola/escola_form/(?P<pk>\d+)/$',escola_form, name='escola_form'),
    url(r'^escola/escola_cadastro/(?P<pk>\d+)/$',escola_cadastro, name='escola_cadastro'),
    url(r'^escola/escolas_list/$', escolas_list, name='escolas_list'),
    # Escola
    # url(r'^escola/(?P<escola_pk>\d+)/professor_form/$', professor_form, name='professor_form'),
    url(r'^escola/(?P<escola_pk>\d+)/professor_form/(?P<professor_pk>\d+)/$', professor_form, name='professor_form'),
    url(r'^escola/(?P<escola_pk>\d+)/professores_list/$', professores_list, name='professores_list'),
    #  Alunos
    #  url(r'^escola/(?P<escola_pk>\d+)/aluno_form/$', aluno_form, name='aluno_form'),
    url(r'^escola/(?P<escola_pk>\d+)/aluno_form/(?P<aluno_pk>\d+)/$', aluno_form, name='aluno_form'),
    url(r'^escola/(?P<escola_pk>\d+)/alunos_list/$', alunos_list, name='alunos_list'),
    #  Classes
    url(r'^escola/(?P<escola_pk>\d+)/classe_form/$', classe_form, name='classe_form'),
    url(r'^escola/(?P<escola_pk>\d+)/classe_form/(?P<classe_pk>\d+)/$', classe_form, name='classe_form'),
    url(r'^escola/(?P<escola_pk>\d+)/classes_list/$', classes_list, name='classes_list'),
]
