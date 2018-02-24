# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from escolar.escolas.models import (
    Escola,
    Aluno,
    MembroFamilia,
)
from xlrd import open_workbook


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('sala')
        parser.add_argument('path')

    def handle(self, *args, **options):
        '''
        ref #50: importar alunos e responsaveis: especies_ alunos_e_responsaveis.odf'

        comando:
        python manage.py import_alunos 7ºano escolas/migrations/alunos_e_responsaveis.odf
        '''
        sheet_name = options['sala']
        planilha = options['path']

        if planilha:
            print('\nImportação de Alunos e Responsáveis da planilha: ', planilha, '\n', 80 * '-')
            self.importa_alunos_e_responsaveis(sheet_name, planilha)
        else:
            raise CommandError(u'\nErro!!')

    def importa_alunos_e_responsaveis(self, sheet_name, planilha):
        """
        workbook.sheet_names()
        [u'7ºano']

        importar alunos e responsaveis de uma planilha.ods'

        criando um Alno ou MembroFamilia para cada linha da planilha
       
        """
        print('importa_alunos_e_responsaveis')
        alunos = 'Zero'
        
        # especies = EspecieTcraFF.objects.all()
        # print u"\nEspécies (antes da importação):", especies.count()
        # try:
        #     print "\nID da última Espécie no BD: ", especies.all().order_by('-id')[0].id, "\n"
        # except:
        #     print " --- "

        # try:
        #     book = open_workbook(planilha)
        #     s = book.sheet_by_name(sheet_name)
        # except:
        #     print u'Ocorreu um erro ao abrir o arquivo, tente novamente'
        # # for s in book.sheets():
        # especies = 0
        # #     # despreza as linhas: 1, 2, 3 == cabeçalho da planilha
        # for row in range(3, s.nrows):
        #     especies += 1
        #     # print s.cell(row, 1), s.cell(row, 2), s.cell(row, 3), s.cell(row, 4)   # Checa a 1ª linha válida
        #     # break
        #     """
        #      'classe_sucessional': u'NP',
        #      'classificacao_plantio': u'D',
        #      'consulta': u'IBOT',
        #      'especie': u'Annona cacans Warm.',
        #      'especie_ameacada': u'LC',
        #      'especie_dispersao': 2L,
        #      'especie_ptr_id': 1325L,
        #      'familia': u'ANACARDIACEAE',
        #      'grupo_plantio': u'D',
        #      'id': 1325L,
        #      'nome_popular': u'guarit\xe1"""
        #     # ##sequencia na planilha [consulta, familia, especie, classe_sucessional,
        #     #                          classificacao_plantio, especie_dispersao, nome_popular,
        #     #                          distribuido, tipo_vegetacao, dominio]
        #     especie, created = EspecieTcraFF.objects.get_or_create(especie=unicode(s.cell(row, 4).value))
        #     if created or especie:
        #         especie.consulta = unicode(s.cell(row, 2).value) or None
        #         especie.familia = unicode(s.cell(row, 3).value) or None
        #         especie.classe_sucessional = unicode(s.cell(row, 12).value) or None
        #         especie.classificacao_plantio = unicode(s.cell(row, 6).value) or None
        #         especie_dispersao_qs = EspecieDispersao.objects.filter(nome=unicode(s.cell(row, 14).value))
        #         if especie_dispersao_qs:
        #             especie.especie_dispersao = especie_dispersao_qs[0]
        #         especie.nome_popular = unicode(s.cell(row, 8).value)

        #         # ## identificando as UF's
        #         unidades_federacao = unicode(s.cell(row, 9).value)
        #         ufs = []
        #         for uf in estados:
        #             if uf in unidades_federacao:
        #                 ufs.append(uf)
        #         distribuido = UF.objects.filter(uf__in=ufs)
        #         # ## adiniona UF
        #         for uf in distribuido:
        #             if uf not in especie.distribuicao.all():
        #                 especie.distribuicao.add(uf)

        #         # ## TIPO de VEGETAÇÃO
        #         tipos_brutos = unicode(s.cell(row, 10).value)
        #         # ##################### na planilha pode começar por ','
        #         if tipos_brutos.startswith(','):
        #             tipos_brutos = tipos_brutos[1:]
        #         # ##################### na planilhha pode estar separado por 'e'
        #         if ' e ' in tipos_brutos:
        #             tipos_brutos = tipos_brutos.replace(' e ', ',')
        #         tipos_brutos = tipos_brutos.split(',')
        #         # tipos_refinados = [t.strip(' ') for t in tipos_brutos]
        #         tipos_vegetacoes = [t.strip(' ') for t in tipos_brutos]
        #         # for tipo_nome in tipos_refinados:
        #         #     if len(tipo_nome) >= 1 and tipo_nome[0] == ' ':
        #         #         tipo_nome = tipo_nome[1:]
        #         #     tipos_vegetacoes.append(tipo_nome)
        #         # ****
        #         #    TipoVegetacao.objects.get_or_create(nome=tipo_nome)

        #         vegetacoes = TipoVegetacao.objects.filter(nome__in=tipos_vegetacoes)
        #         for tipo in vegetacoes:
        #             if tipo not in especie.tipo_vegetacao.all():
        #                 especie.tipo_vegetacao.add(tipo)

        #         # ## DOMINIO FITOGEOGRÁFICOS
        #         dominios_brutos = unicode(s.cell(row, 11).value).split(',')
        #         dominios_nomes = []
        #         for dominio_nome in dominios_brutos:
        #             if len(dominio_nome) >= 1 and dominio_nome[0] == ' ':
        #                 dominio_nome = dominio_nome[1:]
        #             if dominio_nome == u'CER':
        #                 dominio_nome = u'Cerrado'
        #             dominios_nomes.append(dominio_nome)

        #         dominios = DominioFitogeografico.objects.filter(nome__in=dominios_nomes)
        #         for d in dominios:
        #             if d not in especie.dominio.all():
        #                 especie.dominio.add(d)
        #         especie.grupo_plantio = unicode(s.cell(row, 13).value)
        #         especie.especie_ameacada = unicode(s.cell(row, 15).value)

        #         especie.save()

        print('Adicionado: %s especies' % alunos)
        print(80 * '-')
