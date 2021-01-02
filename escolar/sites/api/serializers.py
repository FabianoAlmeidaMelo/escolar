from rest_framework import serializers
from escolar.sites.models import Conteudo


class ConteudoSerializer(serializers.ModelSerializer):

    class Meta:

        model = Conteudo
        fields = ('chave', 'titulo', 'texto', 'foto', 'link')
