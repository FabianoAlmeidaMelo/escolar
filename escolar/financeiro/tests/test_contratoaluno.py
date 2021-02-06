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


class ContratoTest(TestCase):
    '''
    python manage.py test escolar.financeiro.tests.test_contratoaluno
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
            nome='Matrícula',
            descricao='x',
            id=2
        )
        self.categoria_mat_didatico = CategoriaPagamento.objects.create(
            nome='Material Didático',
            descricao='x',
            id=9
        )
        self.curso = Curso.objects.create(
            nome='Primário'
        )
        self.serie = Serie.objects.create(
            curso=self.curso,
            serie='oitava serie'
        )
        self.pessoa_resp = Pessoa.objects.create(
            user_add=self.user,
            user_upd=self.user,
            nascimento=datetime(1975, 10, 10).date(),
            nome='Jair Messias',
            profissao='Engenheiro',
            rg='20465879',
            celular='1298648997',
            cpf='79640286001',
            email='responsavel@gmail.com',
            escola=self.escola,
            nacionalidade='brasileira',
            sexo=1,
        )
        self.membro_familia = MembroFamilia.objects.create(
            user_add=self.user,
            user_upd=self.user,
            pessoa_ptr_id=self.pessoa_resp.id,
            sexo=1,
            escola=self.escola,
            empresa='ZNC',
            obs_empresa='software',
            telefone_empresa='1298987489'
        )

        self.pessoa_aluno = Pessoa.objects.create(
            user_add=self.user,
            user_upd=self.user,
            nascimento=datetime(2005, 12, 10).date(),
            nome='Luzia A Melo',
            profissao='Estudante',
            rg='465789',
            celular='1298566997',
            cpf='19129524083',
            email='aluno@gmail.com',
            escola=self.escola,
            nacionalidade='brasileira',
            sexo=2,
        )
        self.aluno = Aluno.objects.create(
            user_add=self.user,
            user_upd=self.user,
            nascimento=datetime(2005, 12, 10).date(),
            nome='Luzia A Melo',
            profissao='Estudante',
            rg='465789',
            celular='1298566997',
            cpf='19129524083',
            email='aluno@gmail.com',
            escola=self.escola,
            nacionalidade='brasileira',
            sexo=2,
            pessoa_ptr_id=self.pessoa_aluno.id,
            ano=2021,
            curso=self.curso,
            ra='1656568',
        )
        self.responsavel = Responsavel.objects.create(
            membro=self.membro_familia,
            aluno=self.aluno,
            parentesco='Pai',
            responsavel_financeiro=True,
            responsavel_pedagogico=True
        )

        self.contrato = Contrato.objects.create(
            user_add=self.user,
            user_upd=self.user,
            valor=Decimal('6000'),
            ano=2021,
            data_assinatura=datetime(2020, 11, 5),
            nr_parcela=12,
            vencimento=10,
        )
        self.contrato_aluno = ContratoAluno.objects.create(
            user_add=self.user,
            user_upd=self.user,
            valor=Decimal('6000'),
            ano=2021,
            data_assinatura=datetime(2020, 11, 5),
            nr_parcela=12,
            vencimento=10,
            contrato_ptr_id=self.contrato.id,
            multa=Decimal('2'),
            juros=Decimal('2'),
            condicao_juros=2, # por mês
            responsavel=self.membro_familia,
            aluno=self.aluno,
            serie=self.serie,
            desconto=Decimal('10'),
            matricula_valor=Decimal('500'),
            material_valor=Decimal('800'),
            material_parcelas=4,
        )

    def test_str(self):
        self.assertEqual(
            str(self.contrato_aluno),
            "Contrato 2021: Luzia A Melo - Julio Maria"
        )

    def test_parcelas_anuidade(self):
        self.assertEqual(
            self.contrato_aluno.parcelas_anuidade(),
            Decimal('500')
        )

    def test_date_list(self):
        '''
        Gera 12 datas com base no nr de parcelas do contrato,
        ano do contrato
        '''
        date_list = self.contrato_aluno.date_list(
            self.contrato_aluno.nr_parcela
        )
        self.assertEqual(
            len(date_list),
            12
        )
        date_str = [str(data) for data in date_list]
        self.assertEqual(
            date_str,
            ['2021-01-10', '2021-02-10', '2021-03-10', '2021-04-10',
             '2021-05-10', '2021-06-10', '2021-07-10', '2021-08-10',
             '2021-09-10', '2021-10-10', '2021-11-10', '2021-12-10']
        )

    def test_date_list_matricula_2(self):
        '''
        Gera 2 datas com base no nr de parcelas do Matrícula,
        data da matrícula e ano do contrato
        '''
        date_list = self.contrato_aluno.date_list(2, True)
        self.assertEqual(
            len(date_list),
            2
        )
        date_str = [str(data) for data in date_list]
        self.assertEqual(
            date_str,
            ['2020-11-05', '2020-12-10']
        )

    def test_date_list_matricula_4(self):
        date_list = self.contrato_aluno.date_list(4, True)
        self.assertEqual(
            len(date_list),
            4
        )
        date_str = [str(data) for data in date_list]
        self.assertEqual(
            date_str,
            ['2020-11-05', '2020-12-10', '2021-01-10', '2021-02-10' ]
        )

    def test_set_matricula(self):
        self.contrato_aluno.set_matricula(2)
        self.assertEqual(
            Pagamento.objects.filter(
                contrato=self.contrato_aluno,
                tipo=1,
                valor=Decimal('250'),
                nr_parcela__isnull=False,
                categoria=self.categoria
            ).count(),
            2
        )

    def test_set_matricula_uma_parcela(self):
        self.contrato_aluno.set_matricula(1)
        self.assertEqual(
            Pagamento.objects.filter(
                contrato=self.contrato_aluno,
                tipo=1,
                valor=Decimal('500'),
                nr_parcela=None,
                categoria=self.categoria
            ).count(),
            1
        )

    def test_get_resp(self):
        self.assertEqual(
            self.contrato_aluno.get_resp(),
            self.responsavel
        )

    def test_get_valor_extenso(self):
        self.assertEqual(
            self.contrato_aluno.get_valor_extenso(),
            'seis mil reais'
        )

    def test_get_descconto_extenso(self):
        self.assertEqual(
            self.contrato_aluno.get_descconto_extenso(),
            'dez'
        )

    def test_get_datas_parcelas_material(self):
        '''
        4 parcelas sem ParamentosContrato
        '''
        date_list = self.contrato_aluno.get_datas_parcelas_material()
        date_str = [str(data) for data in date_list]

        self.assertEqual(
            len(date_str),
            4
        )
        self.assertEqual(
            date_str,
            ['2021-01-10', '2021-02-10', '2021-03-10', '2021-04-10' ]
        )

    def test_get_datas_parcelas_material_parametros(self):
        '''
        5 parcelas com ParamentosContrato
        '''
        ParametrosContrato.objects.create(
            escola=self.contrato_aluno.aluno.escola,
            ano=self.contrato_aluno.ano,
            material_parcelas=5,
            data_um_material=date(2021, 2, 15),
            data_dois_material=date(2021, 4, 15),
            data_tres_material=date(2021, 6, 15),
            data_quatro_material=date(2021, 8, 15),
            data_cinco_material=date(2021, 10, 15),
            vencimento=10,
            matricula_valor=Decimal('500')

        )
        date_list = self.contrato_aluno.get_datas_parcelas_material()
        date_str = [str(data) for data in date_list]

        self.assertEqual(
            len(date_str),
            5
        )
        self.assertEqual(
            date_str,
            ['2021-02-15', '2021-04-15', '2021-06-15', '2021-08-15', '2021-10-15']
        )