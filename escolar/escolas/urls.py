# coding: utf-8
from django.conf.urls import include, url, patterns

from escolar.escolas.views import (
    escolas_list,
    escola_form,
    grupos_list,
    grupo_form,
    professores_list,
    )

urlpatterns = patterns(
    '',
    # Escola
    url(r'^escolas/escola_form/$', escola_form, name='escola_form'),
    url(r'^escolas/escola_form/(?P<pk>\d+)/$',escola_form, name='escola_form'),
    url(r'^escolas/escolas_list/$', escolas_list, name='escolas_list'),
    # Grupos
    url(r'^escolas/(?P<escola_pk>\d+)/grupo_form/$', grupo_form, name='grupo_form'),
    url(r'^escolas/(?P<escola_pk>\d+)/grupo_form/(?P<grupo_pk>\d+)/$', grupo_form, name='grupo_form'),
    url(r'^escolas/grupos_list/$', grupos_list, name='grupos_list'),
    # Professores
    url(r'^escolas/(?P<escola_pk>\d+)/grupo_form/$', grupo_form, name='grupo_form'),
    url(r'^escolas/(?P<escola_pk>\d+)/grupo_form/(?P<grupo_pk>\d+)/$', grupo_form, name='grupo_form'),
    url(r'^escolas/(?P<escola_pk>\d+)/professores_list/$', professores_list, name='professores_list'),
)
