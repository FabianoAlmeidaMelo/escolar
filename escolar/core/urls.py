# coding: utf-8
from django.conf.urls import include, url

from escolar.core.views import (
    usuarios_list,
    usuario_form,
    # grupo_form,
    # grupos_list,
    )

urlpatterns = [
    # User
    url(r'^escola/(?P<escola_pk>\d+)usuario_form/$', usuario_form, name='usuario_form'),
    url(r'^escola/(?P<escola_pk>\d+)usuario_form/(?P<pk>\d+)/$',usuario_form, name='usuario_form'),
    url(r'^escola/(?P<escola_pk>\d+)/usuarios_list/$', usuarios_list, name='usuarios_list'),

]
