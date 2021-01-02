from rest_framework import generics
from escolar.sites.models import Conteudo
from .serializers import ConteudoSerializer

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
	


@api_view(['GET'])
def conteudo_list(request, escola_pk):
    """
    retorna os conteudos do site da escola
    """
    if request.method == 'GET':
        conteudo = Conteudo.objects.filter(escola_id=escola_pk)
        serializer = ConteudoSerializer(conteudo, many=True)
        return Response(serializer.data)
    else:
    	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)