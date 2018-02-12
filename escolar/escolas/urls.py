# coding: utf-8
from django.conf.urls import url

from escolar.escolas.views import (
    aluno_cadastro,
    aluno_form,
    alunos_list,
    autorizado_cadastro,
    autorizado_form,
    autorizados_list,
    autorizados_aluno_list,
    classes_list,
    classe_form,
    classe_aluno_form,
    classe_professor_form,
    escolas_list,
    escola_cadastro,
    escola_form,
    membro_familia_form,
    professores_list,
    professor_form,
    membros_familia_list,
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
    url(r'^escola/(?P<escola_pk>\d+)/aluno_form/$', aluno_form, name='aluno_form'),
    url(r'^escola/(?P<escola_pk>\d+)/aluno_form/(?P<aluno_pk>\d+)/$', aluno_form, name='aluno_form'),
    url(r'^escola/aluno_cadastro/(?P<aluno_pk>\d+)/$', aluno_cadastro, name='aluno_cadastro'),
    url(r'^escola/(?P<escola_pk>\d+)/alunos_list/$', alunos_list, name='alunos_list'),
    #  Classes
    url(r'^escola/(?P<escola_pk>\d+)/classe_form/$', classe_form, name='classe_form'),
    url(r'^escola/(?P<escola_pk>\d+)/classe_form/(?P<classe_pk>\d+)/$', classe_form, name='classe_form'),
    url(r'^escola/(?P<escola_pk>\d+)/classes_list/$', classes_list, name='classes_list'),
    url(r'^escola/aluno/classe/(?P<classe_pk>\d)/$', classe_aluno_form, name='classe_aluno_form'),
    url(r'^escola/professor/classe/(?P<classe_pk>\d)/$', classe_professor_form, name='classe_professor_form'),
    # Autorizado   responsaveis_list
    url(r'^escola/aluno/(?P<aluno_pk>\d+)/responsavel_form/$', membro_familia_form, name='membro_familia_form'),
    url(r'^escola/aluno/(?P<aluno_pk>\d+)/responsavel/(?P<membro_pk>\d+)/$', membro_familia_form, name='membro_familia_form'),
    url(r'^escola/(?P<aluno_pk>\d+)/responsaveis_list/$', membros_familia_list, name='membros_familia_list'),

    url(r'^escola/(?P<aluno_pk>\d+)/autorizado_form/$', autorizado_form, name='autorizado_form'),
    url(r'^escola/(?P<aluno_pk>\d+)/autorizado/(?P<autorizado_pk>\d+)/$', autorizado_cadastro, name='autorizado_cadastro'),
    url(r'^escola/(?P<aluno_pk>\d+)/autorizado_form/(?P<autorizado_pk>\d+)/$', autorizado_form, name='autorizado_form'),
    url(r'^escola/(?P<escola_pk>\d+)/autorizados_list/$', autorizados_list, name='autorizados_list'),
    url(r'^escola/autorizados_aluno_list/(?P<aluno_pk>\d+)/$', autorizados_aluno_list, name='autorizados_aluno_list'),
]
