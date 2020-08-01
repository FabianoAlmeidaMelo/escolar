# coding: utf-8
from django.conf.urls import url

from escolar.comunicacao.views import (
    cobranca_form,
)

urlpatterns = [
    url(r'^escola/cobranca_form/(?P<pk>\d+)/$', cobranca_form, name='cobranca_form'),
 ]