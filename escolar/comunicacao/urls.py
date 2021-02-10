# coding: utf-8
from django.conf.urls import url

from escolar.comunicacao.views import (
    cobranca_email_form,
    msg_default_form,
    msg_default_list,
    msg_list,
    cobranca_whats_form,
)

urlpatterns = [
    url(r'^escola/msg_list/(?P<escola_pk>\d+)/(?P<contrato_id>\d+)/$', msg_list, name='msg_list'),
    url(r'^escola/msg_default_list/(?P<escola_pk>\d+)/$', msg_default_list, name='msg_default_list'),
    url(r'^escola/(?P<escola_pk>\d+)/msg_default_form/$', msg_default_form, name='msg_default_form'),
    url(r'^escola/(?P<escola_pk>\d+)/msg_default_form/(?P<msg_pk>\d+)/$', msg_default_form, name='msg_default_form'),
    url(r'^escola/cobranca_email_form/(?P<pk>\d+)/$', cobranca_email_form, name='cobranca_email_form'),
    url(r'^escola/cobranca_whats_form/(?P<pk>\d+)/$', cobranca_whats_form, name='cobranca_whats_form'),
 ]