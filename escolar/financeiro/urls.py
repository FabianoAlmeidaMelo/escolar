# coding: utf-8
from django.conf.urls import url

from escolar.financeiro.views import (
	contrato_cadastro,
	contratos_list,
    contratos_aluno_list,
	pagamentos_list,
    pagamentos_aluno_list,
	responsaveis_list,
)

urlpatterns = [
    # Contratos
    url(r'^escola/(?P<aluno_pk>\d+)/contratos_list/$', contratos_list, name='contratos_list'),
    url(r'^escola/(?P<aluno_pk>\d+)/contratos_aluno_list/$', contratos_aluno_list, name='contratos_aluno_list'),
    url(r'^escola/(?P<escola_pk>\d+)/responsaveis_list/$', responsaveis_list, name='responsaveis_list'),
    url(r'^escola/contrato/(?P<contrato_pk>\d+)/$', contrato_cadastro, name='contrato_cadastro'),
    # Pagamentos
    url(r'^escola/(?P<escola_pk>\d+)/pagamentos_list/$', pagamentos_list, name='pagamentos_list'),
    url(r'^escola/pagamentos_aluno_list/(?P<aluno_pk>\d+)/$', pagamentos_aluno_list, name='pagamentos_aluno_list'),
]
