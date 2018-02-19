# coding: utf-8
from django.conf.urls import url

from escolar.financeiro.views import (
    contrato_cadastro,
    contrato_form,
	contratos_list,
    contratos_aluno_list,
    pagamento_form,
	pagamentos_list,
    pagamentos_aluno_list,
    parametro_cadastro,
    parametros_contrato_form,
	responsaveis_list,
    set_pagamento_status,
)

urlpatterns = [
    # Parametros dos Contratos
    url(r'^escola/(?P<escola_pk>\d+)/parametros_cadastro/$', parametro_cadastro, name='parametro_cadastro'),
    url(r'^escola/(?P<escola_pk>\d+)/parametros/$', parametros_contrato_form, name='parametros_contrato_form'),
    # Contratos
    url(r'^escola/(?P<escola_pk>\d+)/contratos_list/$', contratos_list, name='contratos_list'),
    url(r'^escola/(?P<aluno_pk>\d+)/contratos_aluno_list/$', contratos_aluno_list, name='contratos_aluno_list'),
    url(r'^escola/(?P<escola_pk>\d+)/responsaveis_list/$', responsaveis_list, name='responsaveis_list'),
    
    url(r'^escola/aluno/(?P<aluno_pk>\d+)/contrato/form/$', contrato_form, name='contrato_form'),
    url(r'^escola/aluno/(?P<aluno_pk>\d+)/contrato/(?P<contrato_pk>\d+)/$', contrato_form, name='contrato_edit'),
    url(r'^escola/contrato/(?P<contrato_pk>\d+)/$', contrato_cadastro, name='contrato_cadastro'),
    # Pagamentos
    url(r'^escola/(?P<escola_pk>\d+)/pagamentos_list/$', pagamentos_list, name='pagamentos_list'),
    url(r'^escola/pagamentos_aluno_list/(?P<aluno_pk>\d+)/$', pagamentos_aluno_list, name='pagamentos_aluno_list'),
    url(r'^escola/(?P<escola_pk>\d+)/pagamento_form/$', pagamento_form, name='pagamento_form'),
    url(r'^escola/(?P<escola_pk>\d+)/pagamento/(?P<pagamento_pk>\d+)/$', pagamento_form, name='pagamento_edit'),
    url(r'^escola/(?P<escola_pk>\d+)/contrato/(?P<contrato_pk>\d+)/pagamento_form/$', pagamento_form, name='pagamento_contrato_form'),
    url(r'^escola/(?P<escola_pk>\d+)/contrato/(?P<contrato_pk>\d+)pagamento/(?P<pagamento_pk>\d+)/$', pagamento_form, name='pagamento_aluno_edit'),
    url(r'^escola/pagamento/(?P<pagamento_pk>\d+)/set_status/$', set_pagamento_status, name="set_pagamento_status"
        ),
]
