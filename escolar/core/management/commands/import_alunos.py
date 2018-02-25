# -*- coding: utf-8 -*-
from xlrd import open_workbook
from django.core.management.base import BaseCommand, CommandError

from escolar.escolas.models import (
    Escola,
    Aluno,
    MembroFamilia,
)
from escolar.core.models import Endereco


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('slug') # crescer_sjc
        parser.add_argument('sala')
        parser.add_argument('path')

    def handle(self, *args, **options):
        '''
        ref #50: importar alunos e responsaveis: especies_ alunos_e_responsaveis.odf'

        comando:
        python manage.py import_alunos SLUG_ESCOLA SALA escolar/escolas/migrations/PLANILHA.xls
        python manage.py import_alunos crescer_sjc setima escolar/escolas/migrations/alunos_e_responsaveis.xls
        '''
        slug = options['slug']
        sheet_name = options['sala']
        planilha = options['path']

        if planilha:
            print('\nImportação de Alunos e Responsáveis da planilha: ', planilha, '\n', 80 * '-')
            self.importa_alunos_e_responsaveis(slug, sheet_name, planilha)
        else:
            raise CommandError(u'\nErro!!')

    def importa_alunos_e_responsaveis(self, slug, sheet_name, planilha):
        """
        workbook.sheet_names()
        [u'7ºano']

        importar alunos e responsaveis de uma planilha.ods'

        criando um Alno ou MembroFamilia para cada linha da planilha
       
        """
        print('importa_alunos_e_responsaveis')
        escola = Escola.objects.get(slug=slug)
        alunos = Aluno.objects.all()
        responsaveis = MembroFamilia.objects.all()
        enderecos = Endereco.objects.all()
        print("\nAlunos (antes da importação):", alunos.count())
        print("\nResponsáveis (antes da importação):", responsaveis.count())
        print("\nEndereços (antes da importação):", enderecos.count())
        try:
            print("\nID da última Aluno no BD: ", alunos.all().order_by('-id')[0].id, "\n")
        except:
            print(" --- ")

        book = open_workbook(planilha)
        s = book.sheet_by_name(sheet_name)

        # for s in book.sheets():
        linhas = 0
        #     # despreza as linhas: 1, 2 == cabeçalho da planilha
        for row in range(2, s.nrows):
            linhas += 1
            # Checa a 1ª linha válida
            # ABCDEFGHIJKJLMNOP
            # print (s.cell(row, 0),  # A   'PERFIL'
            #        s.cell(row, 1),  # B   'RA'
            #        s.cell(row, 2),  # C   'NOME'
            #        s.cell(row, 3),  # D   'E-MAIL'
            #        s.cell(row, 4),   # E   'RESP FIN'
            #        s.cell(row, 5),  # F   'RESP PED' 
            #        s.cell(row, 6),  # G   'SEXO' 
            #        s.cell(row, 7),  # H   'DATA NASC'
            #        s.cell(row, 8),  # I   'CPF'
            #        s.cell(row, 9),  # J   'RG'
            #        s.cell(row, 10), # K   'CELULAR' 
            #        s.cell(row, 11), # L   'CIDADE'
            #        s.cell(row, 12), # M   'RUA'
            #        s.cell(row, 13), # N   'NUMERO'
            #        s.cell(row, 14), # O   'BAIRRO'
            #        s.cell(row, 15)) # P   'CEP' 

            perfil = s.cell(row, 0)
            ra = s.cell(row, 1)
            nome = s.cell(row, 2)
            email = s.cell(row, 3)
            resp_fin = s.cell(row, 4).lower()
            responsavel_financeiro = resp_fin == 'sim'
            resp_ped = s.cell(row, 5)
            responsavel_pedagogico = resp_ped == 'sim'
            sexo = 1 if s.cell(row, 6).lower() == 'm' else 2
            nascimento = s.cell(row, 7)    # H   'DATA NASC'
            s.cell(row, 8)    # I   'CPF'
            s.cell(row, 9)    # J   'RG'
            s.cell(row, 10)   # K   'CELULAR' 
            s.cell(row, 11)   # L   'CIDADE'
            s.cell(row, 12)   # M   'RUA'
            s.cell(row, 13)   # N   'NUMERO'
            s.cell(row, 14)   # O   'BAIRRO'
            s.cell(row, 15)   # P   'CEP' 

            if perfil == 'Aluno':
                aluno, created = Aluno.objects.get_or_create(escola=escola, ra=)
            

        print('Adicionado: %s Alunos' % linhas)
        print('Adicionado: %s Responsáveis' % linhas)
        print(80 * '-')
