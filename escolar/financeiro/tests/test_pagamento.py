from datetime import datetime, date
from django.test import TestCase

from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import resolve_url
from escolar.core.models import Pais
from escolar.escolas.models import (
    Aluno,
    Curso,
    Escola,
    MembroFamilia,
    Pessoa,
    Responsavel,
    Serie,
)

from escolar.financeiro.models import (
    CONDICAO_DESCONTO,
    CategoriaPagamento,
    Contrato,
    ContratoAluno,
    DIA_UTIL,
    FORMA_PGTO,
    JUROS_EXPECIFICACAO,
    Pagamento,
    ParametrosContrato,
)

from escolar.core.models import (
    Group,
    UserGrupos,
    User,
)

from municipios.models import Municipio, UF
from decimal import Decimal


class PagamentoTest(TestCase):
    '''
    python manage.py test escolar.financeiro.tests.test_pagamento
    '''
    def setUp(self):
        self.grupo = Group.objects.create(
            name='Admin'
        )

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

        self.user = User.objects.create(
            email='user@gmail.com',
            username='user@gmail.com',
            nome='Fabiano',
        )
        UserGrupos.objects.create(
            escola=self.escola,
            user=self.user,
            grupo=self.grupo,
            ativo=True
        )
        self.categoria = CategoriaPagamento.objects.create(
            nome='Aguá',
            descricao='Conta de água e esgoto',
        )
        self.pagamento = Pagamento.objects.create(
            escola=self.escola,
            titulo='Conta de Água',
            data=date(2021,4,2),
            valor=Decimal('99.9'),
            data_pag=date(2021,4,2),
            observacao='Pagamento recorrente',
            tipo=2,
            taxa_cartao=10

        )


    def test_str(self):
        self.assertEqual(
            str(self.pagamento),
            "Conta de Água"
        )

    def test_get_valor_liquido(self):
        self.assertEqual(
            self.pagamento.get_valor_liquido(),
            Decimal('99.9')
        )

    def test_get_valor_liquido_2(self):
        # efetivado
        self.pagamento.efet = True
        self.pagamento.save()
        self.assertEqual(
            self.pagamento.get_valor_liquido(),
            Decimal('89.91')
        )

    def test_get_valor_extenso(self):
        self.assertEqual(
            self.pagamento.get_valor_extenso(),
            'noventa e nove reais e noventa centavos'
        )

    def test_get_tipo_display(self):
        self.assertEqual(
            self.pagamento.get_tipo_display(),
            '(-)'
        )

    def test_get_tipo_display_2(self):
        self.pagamento.tipo = 1
        self.pagamento.save()
        self.assertEqual(
            self.pagamento.get_tipo_display(),
            '(+)'
        )

    def test_get_color_display(self):
        self.assertEqual(
            self.pagamento.get_color_display(),
            'red'
        )


    def test_get_color_display_blue(self):
        self.pagamento.tipo = 1
        self.pagamento.save()
        self.assertEqual(
            self.pagamento.get_color_display(),
            'blue'
        )

    def test_get_color_display_black(self):
        self.pagamento.tipo = None
        self.pagamento.save()
        self.assertEqual(
            self.pagamento.get_color_display(),
            'black'
        )

    def test_gerar_complementar(self):
        previsto = self.pagamento.valor
        data = date(
            self.pagamento.data.year,
            self.pagamento.data.month + 1,
            self.pagamento.data.day
        )
        valor = Decimal('50')
        obs = 'pagou a metade'
        parcela_id = self.pagamento.id
        self.pagamento.valor = Decimal('49.90')
        self.pagamento.efet = True
        self.pagamento.save()
        self.pagamento.gerar_complementar(
            previsto,
            data,
            valor,
            obs
        )

        complementar =Pagamento.objects.filter(
            parcela_id=parcela_id
        ).first()
        self.assertEqual(
            complementar.valor,
            Decimal('50')
        )

    def test_gerar_replicas(self):
        parcela_id = self.pagamento.id
        self.pagamento.efet = True
        self.pagamento.save()
        self.pagamento.gerar_replicas(
            11
        )
        '''
        pediu 11 mas isso ultrapassaria o ano corrente
        pois a data do original é Abril
        '''

        qtd_replicas = Pagamento.objects.filter(
            parcela_id=parcela_id
        ).count()
        self.assertEqual(
            qtd_replicas,
            8
        )

    def test_gerar_replicas_4(self):
        parcela_id = self.pagamento.id
        self.pagamento.efet = True
        self.pagamento.save()
        self.pagamento.gerar_replicas(
            4
        )

        qtd_replicas = Pagamento.objects.filter(
            parcela_id=parcela_id
        ).count()
        self.assertEqual(
            qtd_replicas,
            4
        )