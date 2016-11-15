from datetime import datetime
from django.test import TestCase

from escolar.escolas.models import Escola
from municipios.models import Municipio, UF

class EscolaModelTest(TestCase):
    def setUp(self):
        self.uf = UF(id_ibge=1234,
                     uf='SP',
                     nome='São Paulo',
                     regiao='Sudeste',
                )
        self.municipio = Municipio(
            id_ibge=12233,
            nome_abreviado='SJC',
            nome="São José dos Campos",
            uf=self.uf,
            uf_sigla='SP',
            )
        self.obj = Escola(nome='Padre Julio Maria',
                          endereco='rua xyz',
                          numero='123A',
                          telefone='12-31247895',
                          bairro='Santana',
                          municipio=self.municipio,
                        )
        self.obj.save()

    def test_create(self):
        """TESTE 01 test_model_escola"""
        self.assertTrue(Escola.objects.exists())

