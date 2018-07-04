# coding: utf-8
from django.conf.urls import url

from escolar.escolas.views import (
    aluno_cadastro,
    aluno_ficha_matricula,
    aluno_form,
    aluno_historico,
    alunos_list,
    aniversariantes_list,
    autorizado_cadastro,
    autorizado_form,
    autorizados_aluno_list,
    autorizados_list,
    classe_aluno_form,
    classe_form,
    classe_professor_form,
    classes_list,
    escola_cadastro,
    escola_form,
    escolas_list,
    membro_familia_cadastro,
    membro_familia_form,
    membros_familia_list,
    parabens_form,
    professor_form,
    professores_list,
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

    #  Alunos  aluno_historico
    url(r'^escola/(?P<escola_pk>\d+)/aluno_form/$', aluno_form, name='aluno_form'),
    url(r'^escola/(?P<escola_pk>\d+)/aluno_form/(?P<aluno_pk>\d+)/$', aluno_form, name='aluno_form'),
    url(r'^escola/aluno_cadastro/(?P<aluno_pk>\d+)/$', aluno_cadastro, name='aluno_cadastro'),
    url(r'^escola/(?P<escola_pk>\d+)/alunos_list/$', alunos_list, name='alunos_list'),
    url(r'^escola/ficha_matricula/aluno/(?P<aluno_pk>\d+)$', aluno_ficha_matricula, name='aluno_ficha_matricula'),
    url(r'^escola/historico/aluno/(?P<aluno_pk>\d+)/$', aluno_historico, name='aluno_historico'),
    #  Classes
    url(r'^escola/(?P<escola_pk>\d+)/classe_form/$', classe_form, name='classe_form'),
    url(r'^escola/(?P<escola_pk>\d+)/classe_form/(?P<classe_pk>\d+)/$', classe_form, name='classe_form'),
    url(r'^escola/(?P<escola_pk>\d+)/classes_list/$', classes_list, name='classes_list'),
    url(r'^escola/aluno/classe/(?P<classe_pk>\d)/$', classe_aluno_form, name='classe_aluno_form'),
    url(r'^escola/professor/classe/(?P<classe_pk>\d)/$', classe_professor_form, name='classe_professor_form'),
    # responsaveis_list
    url(r'^escola/aluno/(?P<aluno_pk>\d+)/responsavel_form/$', membro_familia_form, name='membro_familia_form'),
    url(r'^escola/aluno/(?P<aluno_pk>\d+)/responsavel_edit/(?P<membro_pk>\d+)/(?P<responsavel_pk>\d+)/$', membro_familia_form, name='membro_familia_form'),
    url(r'^escola/aluno/(?P<aluno_pk>\d+)/responsavel/(?P<membro_pk>\d+)/(?P<responsavel_pk>\d+)/$', membro_familia_cadastro, name='membro_familia_cadastro'),
    url(r'^escola/(?P<aluno_pk>\d+)/responsaveis_list/$', membros_familia_list, name='membros_familia_list'),

    # Autorizados
    url(r'^escola/(?P<aluno_pk>\d+)/autorizado_form/$', autorizado_form, name='autorizado_form'),
    url(r'^escola/(?P<aluno_pk>\d+)/autorizado/(?P<autorizado_pk>\d+)/$', autorizado_cadastro, name='autorizado_cadastro'),
    url(r'^escola/(?P<aluno_pk>\d+)/autorizado_form/(?P<autorizado_pk>\d+)/$', autorizado_form, name='autorizado_form'),
    url(r'^escola/(?P<escola_pk>\d+)/autorizados_list/$', autorizados_list, name='autorizados_list'),
    url(r'^escola/autorizados_aluno_list/(?P<aluno_pk>\d+)/$', autorizados_aluno_list, name='autorizados_aluno_list'),
    # aniversariantes, Pessoas
    url(r'^escola/(?P<escola_pk>\d+)/aniversariantes_list/$', aniversariantes_list, name='aniversariantes_list'),
    url(r'^escola/(?P<pessoa_pk>\d+)/parabens_form/$', parabens_form, name='parabens_form'),
]
