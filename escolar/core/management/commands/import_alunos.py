# -*- coding: utf-8 -*-
import time
from xlrd import open_workbook
from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from escolar.escolas.models import (
    Aluno,
    Escola,
    MembroFamilia,
    Responsavel,
)
from escolar.core.models import Endereco
from escolar.escolas.forms import set_only_number
from municipios.models import Municipio
from escolar.core.models import User

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
        python manage.py import_alunos_v2 SLUG_ESCOLA SALA escolar/escolas/migrations/PLANILHA.xls
        **
        python manage.py import_alunos_v2 crescer_sjc setima escolar/escolas/migrations/alunos_e_responsaveis.xls
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
        # USER
        # TODO: DEVE SER O DONO DA ESCOLA OU DIRETOR:
        user = User.objects.filter(username='colegio.crescer.contabil@gmail.com').last()
        print('importa_alunos_e_responsaveis')
        escola = Escola.objects.get(slug=slug)
        municipio = Municipio.objects.get(id_ibge=3549904)  # são josé dos campos
        alunos = Aluno.objects.all()
        responsaveis = MembroFamilia.objects.all()
        enderecos = Endereco.objects.all()
        print("\nAlunos (antes da importação):", alunos.count())
        print("\nResponsáveis (antes da importação):", responsaveis.count())
        print("\nEndereços (antes da importação):", enderecos.count())
        try:
            print("\nID do última Aluno no BD: ", alunos.all().order_by('-id')[0].id, "\n")
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

            perfil = (s.cell(row, 0).value or '').strip().lower()
            ra = (s.cell(row, 1).value or '').strip()
            nome = (s.cell(row, 2).value or '').strip()
            email = (s.cell(row, 3).value or '').strip()
            resp_fin = (s.cell(row, 4).value or '').strip().lower()

            responsavel_financeiro = resp_fin == 'sim'

            resp_ped = (s.cell(row, 5).value or '').strip().lower()
            responsavel_pedagogico = resp_ped == 'sim'

            sexo = 1 if (s.cell(row, 6).value or '').strip().lower() == 'm' else 2
            data_planilha = (s.cell(row, 7).value or '' or 0)
            nascimento = date.fromtimestamp(data_planilha*86400) - SETENTA_ANOS if data_planilha else None
            cpf = (s.cell(row, 8).value or '').strip()    # I   'CPF'

            if cpf:
                cpf = set_only_number(cpf)
            rg = int(s.cell(row, 9).value) if type(s.cell(row, 9).value or '') == float else (s.cell(row, 9).value or '').strip()   # J   'RG'
            if rg:
                rg = set_only_number(rg).strip()
            celular = (s.cell(row, 10).value or '').strip().replace(" ", "")   # K   'CELULAR' 
             
            logradouro = (s.cell(row, 12).value or '').strip()   # M   'RUA'
            numero = str(int(s.cell(row, 13).value)).strip() if type(s.cell(row, 13).value or '') == float else (s.cell(row, 13).value or '').strip()  # N   'NUMERO'
            bairro = (s.cell(row, 14).value or '').strip()   # O   'BAIRRO'
            cep = str(int(s.cell(row, 15).value)).strip() if type(s.cell(row, 15).value or '') == float else (s.cell(row, 15).value or '').strip()   # P   'CEP' 
            observacao = sheet_name # sala
            
            # print(perfil, logradouro, numero, bairro, cep)

            if perfil == 'aluno':
                aluno, aluno_created = Aluno.objects.update_or_create(escola=escola,
                                                                      ra=ra, defaults={
                                                                      'nascimento':nascimento,
                                                                      'natural_municipio': municipio,
                                                                      'nome':nome,
                                                                      'nacionalidade':'brasileira',
                                                                      'email':email,
                                                                      'cpf':cpf,
                                                                      'rg':rg,
                                                                      'sexo':sexo,
                                                                      'user_add':user,
                                                                      'user_upd':user,
                                                                      'observacao':observacao,
                                                                      })
                if aluno and not aluno.endereco:
                    endereco, endereco_created = Endereco.objects.update_or_create(logradouro=logradouro,
                                                                                   municipio=municipio,
                                                                                   numero=numero,
                                                                                   bairro=bairro,
                                                                                   cep=cep)
                    aluno.endereco = endereco
                    aluno.save()
            else:
                aluno = Aluno.objects.filter(ra=ra, escola=escola).last()
                if aluno and aluno.responsavel_set.filter(membro__cpf=cpf).count() == 0:
                    membro, membro_created = MembroFamilia.objects.update_or_create(escola=escola,
                                                                                    nome=nome,
                                                                                    cpf=cpf, defaults={
                                                                                    'nascimento':nascimento,
                                                                                    'natural_municipio': municipio,
                                                                                    'email':email,
                                                                                    'rg':rg,
                                                                                    'sexo':sexo,
                                                                                    'celular':celular,
                                                                                    'user_add':user,
                                                                                    'user_upd':user,
                                                                                    })
                    if aluno and membro:
                        responsavel, resp_created = Responsavel.objects.update_or_create(parentesco=perfil,
                                                                                         aluno=aluno,
                                                                                         membro=membro,
                                                                                         responsavel_financeiro=responsavel_financeiro,
                                                                                         responsavel_pedagogico=responsavel_pedagogico)
            

        print('Adicionado: %s Alunos' % Aluno.objects.all().count())
        print('Adicionado: %s Responsáveis' % MembroFamilia.objects.all().count())
        print(80 * '-')
