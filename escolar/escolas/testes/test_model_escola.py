from datetime import datetime
from django.test import TestCase

from escolar.escolas.models import Escola
from municipios.models import Municipio, UF

class EscolaModelTest(TestCase):
    def setUp(self):
        # self.uf = UF(id_ibge=1234,
        #              uf='SP',
        #              nome='São Paulo',
        #              regiao='Sudeste',
        #         )
        # self.municipio = Municipio(
        #     id_ibge=12233,
        #     nome_abreviado='SJC',
        #     nome="São José dos Campos",
        #     uf=self.uf,
        #     uf_sigla='SP',
        #     )
        self.escola = Escola(nome='Padre Julio Maria',
                             endereco='rua xyz',
                             numero='123A',
                             telefone='12-31247895',
                             bairro='Santana',
                             # municipio=self.municipio,
                        )
        self.escola.save()

    def test_create(self):
        """TESTE 01 test_model_escola"""
        self.assertTrue(Escola.objects.exists())

    def test_created_at(self):
        """Escola must have an auto created_at attr"""
        self.assertIsInstance(self.escola.created_at, datetime)

    def test_str(self):
        self.assertEqual('Padre Julio Maria', str(self.escola))
