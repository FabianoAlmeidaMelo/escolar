from datetime import datetime
from django.test import TestCase

from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import resolve_url
from escolar.core.models import Pais
from escolar.escolas.models import Escola
from escolar.sites.models import Conteudo
from municipios.models import Municipio, UF


class ConteudoTest(TestCase):
    '''
    python manage.py test escolar.sites.tests.test_conteudo
    '''
    def setUp(self):
        self.pais = Pais(nome='Brasil',
                         sigla='BRA',
                         idioma='português',)
        self.pais.save()
        self.uf = UF(id_ibge=1234,
                     uf='SP',
                     nome='São Paulo',
                     regiao='Sudeste',)
        self.uf.save()
        self.municipio = Municipio(
            id_ibge=12233,
            nome_abreviado='SJC',
            nome="São José dos Campos",
            uf=self.uf,
            uf_sigla='SP',)
        self.municipio.save()
        self.escola = Escola(
            pais=self.pais,
            nome='Padre Julio Maria',
            razao_social='Pde julio S/A',
            endereco='rua xyz',
            numero='123A',
            telefone='12-31247895',
            municipio=self.municipio,
            bairro='Santana',
            celular='12982239764',
            slug='padre_julio',
        )
        self.escola.save()

        self.image = SimpleUploadedFile("delicious.jpeg", b"something tasty")
        self.conteudo = Conteudo.objects.create(
            escola=self.escola,
            chave='Photo',
            titulo='Primeira foto',
            foto=self.image,
            ordem=1
        )

    def test_api_conteudo_get(self):
        url = '/sites/api/conteudo/%s/' % self.escola.id
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_api_conteudo_post(self):
       url = '/sites/api/conteudo/%s/' % self.escola.id
       response = self.client.post(url)
       self.assertEqual(405, response.status_code)

    def test_api_conteudo_put(self):
       url = '/sites/api/conteudo/%s/' % self.escola.id
       response = self.client.put(url)
       self.assertEqual(405, response.status_code)