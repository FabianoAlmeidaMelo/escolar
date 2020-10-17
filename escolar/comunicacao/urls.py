# coding: utf-8
from django.conf.urls import url

from escolar.comunicacao.views import (
    cobranca_form,
    msg_default_form,
    msg_list,
    msg_default_list,
)

urlpatterns = [
	url(r'^escola/msg_list/(?P<escola_pk>\d+)/(?P<contrato_id>\d+)/$', msg_list, name='msg_list'),
    url(r'^escola/msg_default_list/(?P<escola_pk>\d+)/$', msg_default_list, name='msg_default_list'),
    url(r'^escola/(?P<escola_pk>\d+)/msg_default_form/$', msg_default_form, name='msg_default_form'),
    url(r'^escola/(?P<escola_pk>\d+)/msg_default_form/(?P<msg_pk>\d+)/$', msg_default_form, name='msg_default_form'),
    url(r'^escola/cobranca_form/(?P<pk>\d+)/$', cobranca_form, name='cobranca_form'),
 ]