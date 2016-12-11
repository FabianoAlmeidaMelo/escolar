# coding: utf-8
from django.conf.urls import include, url, patterns

from escolar.escolas.views import (
    escolas_list,
    escola_form,
    )

urlpatterns = patterns(
    '',
    url(r'^escolas/escola_form/$', escola_form, name='escola_form'),
    url(r'^escolas/escola_form/(?P<pk>\d+)/$',escola_form, name='escola_form'),
    url(r'^escolas/escolas_list/$', escolas_list, name='escolas_list'),
)
