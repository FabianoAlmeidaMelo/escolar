from django.conf.urls import url
from .views import conteudo_list

urlpatterns = [
	url(r'^sites/api/conteudo/(?P<escola_pk>\d+)/$', conteudo_list, name='conteudo'),
]