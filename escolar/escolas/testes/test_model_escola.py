from datetime import datetime
from django.test import TestCase

from escolar.escolas.models import Escola
from municipios.models import Municipio, UF
from escolar.core.models import Pais

'''
python manage.py test escolar.escolas.testes.test_model_escola
'''

class EscolaModelTest(TestCase):
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
        self.escola = Escola(pais=self.pais,
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

    def test_create(self):
        """TESTE 01 test_model_escola"""
        self.assertTrue(Escola.objects.exists())

    def test_created_at(self):
        """Escola must have an auto created_at attr"""
        self.assertIsInstance(self.escola.created_at, datetime)

    def test_str(self):
        self.assertEqual('Padre Julio Maria', str(self.escola))

    def test_publica(self):
        self.assertEqual(False, self.escola.publica)
