from datetime import datetime
from django.test import TestCase

from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import resolve_url
from escolar.core.models import Pais
from escolar.escolas.models import Escola
from escolar.financeiro.models import (
    Bandeira,
    escola_contrato_path,
    FORMA_PGTO,
    CONDICAO_DESCONTO,
    JUROS_EXPECIFICACAO,
    DIA_UTIL
)
from municipios.models import Municipio, UF


class BandeiraTest(TestCase):
    '''
    python manage.py test escolar.financeiro.tests.test_bandeira

    testa a model Bandeira
    CONSTANTES e algumas funções
    '''
    def setUp(self):
        self.pais = Pais(
            nome='Brasil',
            sigla='BRA',
            idioma='português'
        )
        self.pais.save()
        self.uf = UF(
            id_ibge=1234,
            uf='SP',
            nome='São Paulo',
            regiao='Sudeste'
        )
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
            nome='Julio Maria',
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
        for nome in ['Visa', 'Mastercard', 'Cielo']:
            Bandeira.objects.create(
                escola=self.escola,
                nome=nome
            )

    def test_str(self):
        bandeira = Bandeira.objects.get(nome='Visa')
        self.assertEqual(str(bandeira), 'Julio Maria - Visa')
        bandeira.escola = None
        bandeira.save()
        self.assertEqual(str(bandeira), 'Visa')

    def test_FORMA_PGTO(self):
        self.assertEqual(len(FORMA_PGTO), 9)
        opcoes = [
            '--',
            'boleto bancário',
            'cartão de crédito',
            'cartão de débito',
            'cheque',
            'dinheiro',
            'permuta',
            'transferência bancária',
            'pix'
        ]
        for forma in FORMA_PGTO:
            self.assertTrue(
                forma[1] in opcoes
            )

    def test_CONDICAO_DESCONTO(self):
        self.assertEqual(len(CONDICAO_DESCONTO), 3)
        opcoes = [
            '--',
            'Pagamento até a data vencimento',
            'Pagamento até determinado dia útil',
        ]
        for condicao in CONDICAO_DESCONTO:
            self.assertTrue(
                condicao[1] in opcoes
            )

    def test_JUROS_EXPECIFICACAO(self):
        self.assertEqual(len(JUROS_EXPECIFICACAO), 3)
        opcoes = [
            '--',
            'pro rata die',
            'Por Mês',
        ]
        for obj in JUROS_EXPECIFICACAO:
            self.assertTrue(
                obj[1] in opcoes
            )

    def test_JUROS_EXPECIFICACAO(self):
        self.assertEqual(len(DIA_UTIL), 13)
        opcoes = [
            '--',
            '1º',
            '2º',
            '3º',
            '4º',
            '5º',
            '6º',
            '7º',
            '8º',
            '9º',
            '10º',
            '11º',
            '12º'
        ]
        for dia in DIA_UTIL:
            self.assertTrue(
                dia[1] in opcoes
            )
