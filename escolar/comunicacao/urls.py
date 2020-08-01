# coding: utf-8
from django.conf.urls import url

from escolar.comunicacao.views import (
    cobranca_form,
    msg_default_list,
)

urlpatterns = [
    url(r'^escola/msg_default_list/(?P<escola_pk>\d+)/$', msg_default_list, name='msg_default_list'),
    url(r'^escola/cobranca_form/(?P<pk>\d+)/$', cobranca_form, name='cobranca_form'),
 ]