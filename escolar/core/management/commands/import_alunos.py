# -*- coding: utf-8 -*-
import time
from xlrd import open_workbook
from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from escolar.escolas.models import (
    Escola,
    Aluno,
    MembroFamilia,
)
from escolar.core.models import Endereco
from escolar.escolas.forms import set_only_number
from municipios.models import Municipio

SETENTA_ANOS = datetime(1970, 1, 1) - datetime(1900, 1, 1) + timedelta(days=1)

class Command(BaseCommand):
    DATE_FTMS = ('%Y%m%d', '%d/%m/%Y', '%d/%m/%Y %H:%M', '%d/%m/%Y %H:%M:%S',)

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

    def get_date(self, value, formats=DATE_FTMS):
        date_value = None
        if value:  # pode vir None ou ''
            for fmt in formats:
                try:
                    date_value = date(*time.strptime(value, fmt)[:3])
                    break
                except ValueError:
                    pass
        return date_value

    def importa_alunos_e_responsaveis(self, slug, sheet_name, planilha):
        """
        workbook.sheet_names()
        [u'7ºano']

        importar alunos e responsaveis de uma planilha.ods'

        criando um Alno ou MembroFamilia para cada linha da planilha
       
        """
        print('importa_alunos_e_responsaveis')
        escola = Escola.objects.get(slug=slug)
        municipio = Municipio.objects.get(id_ibge=3549904)
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

            perfil = (s.cell(row, 0).value).strip().lower()
            ra = (s.cell(row, 1).value).strip()
            nome = (s.cell(row, 2).value).strip()
            email = (s.cell(row, 3).value).strip()
            resp_fin = (s.cell(row, 4).value).strip().lower()
            responsavel_financeiro = resp_fin == 'sim'
            resp_ped = (s.cell(row, 5).value).strip().lower()
            responsavel_pedagogico = resp_ped == 'sim'
            sexo = 1 if (s.cell(row, 6).value).strip().lower() == 'm' else 2
            data_planilha = (s.cell(row, 7).value or 0)
            nascimento = date.fromtimestamp(data_planilha*86400) - SETENTA_ANOS if data_planilha else None
            cpf = str(s.cell(row, 8)).strip()    # I   'CPF'
            if cpf:
                cpf = set_only_number(cpf)
            rg = str(s.cell(row, 9))    # J   'RG'
            if rg:
                rg = set_only_number(rg).strip()
            celular = str(s.cell(row, 10)).strip()   # K   'CELULAR' 
             #str(s.cell(row, 11))   # L   'CIDADE'
            logradouro = str(s.cell(row, 12)).strip()   # M   'RUA'
            numero = str(s.cell(row, 13)).strip()   # N   'NUMERO'
            bairro = str(s.cell(row, 14)).strip()   # O   'BAIRRO'
            cep = str(s.cell(row, 15)).strip()   # P   'CEP' 
            # print(perfil, data_planilha, nascimento)

            if perfil == 'aluno':
                aluno, aluno_created = Aluno.objects.get_or_create(escola=escola,
                                                             ra=ra,
                                                             nascimento=nascimento,
                                                             nome=nome,
                                                             nacionalidade='brasileira',
                                                             email=email,
                                                             cpf=cpf,
                                                             rg=rg,
                                                             sexo=sexo)
                if aluno_created:
                    endereco, endereco_created = Endereco.objects.get_or_create(logradouro=logradouro,
                                                                                municipio=municipio,
                                                                                numero=numero,
                                                                                bairro=bairro,
                                                                                cep=cep)
            else:
                aluno = Aluno.objects.get(ra=ra)
                if aluno.
                responsavel = MembroFamilia.objects.get_or_create(parentesco=perfil,
                                                                  aluno=aluno,
                                                                  nome=nome, defaults={
                                                                  'nascimento':nascimento,
                                                                  'responsavel_financeiro':responsavel_financeiro,
                                                                  'responsavel_pedagogico':responsavel_pedagogico,
                                                                  'email':email,
                                                                  'cpf':cpf,
                                                                  'rg':rg,
                                                                  'sexo':sexo,
                                                                  'celular':celular})
            

        print('Adicionado: %s Alunos' % Aluno.objects.all().count())
        print('Adicionado: %s Responsáveis' % MembroFamilia.objects.all().count())
        print(80 * '-')
