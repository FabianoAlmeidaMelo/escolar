# coding: utf-8
from django.conf.urls import url

from escolar.sites.views import (
    conteudo_form,
    conteudo_list,
)

urlpatterns = [
    url(r'^escola/conteudo_form/(?P<escola_pk>\d+)/$', conteudo_form, name='conteudo_form'),
    url(r'^escola/conteudo_form/(?P<escola_pk>\d+)/(?P<conteudo_pk>\d+)/$', conteudo_form, name='conteudo_edit'),
    url(r'^escola/conteudo_list/(?P<escola_pk>\d+)/$', conteudo_list, name='conteudo_list'),
 ]