# coding: utf-8
from django.conf.urls import include, url, patterns

from escolar.escolas.views import escolas_list

urlpatterns = patterns(
    '',
    # url(r'^palestras/$', talk_list, name='talk_list'),
    url(r'^escolas_list/$', escolas_list, name='escolas_list'),
    # url(
    #     r'^agenda_list/$',
    #     'helper.agenda.views.agenda_list', name='agenda_list'
    #     ),
    # url(r'^(\d+)/$', detail, name='detail'),
)
