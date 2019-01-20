# -*- coding: utf-8 -*-
import time

from datetime import date, datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from datetime import date
from decimal import Decimal
from escolar.financeiro.models import ContratoAluno, CategoriaPagamento, Pagamento


class Command(BaseCommand):

    def handle(self, *args, **options):
        '''
        ref #103
        Pagamento.objects.filter(contrato__ano=2019).count()
        9 Material Didático

        1 0 a 2 anos R$ 165,00
        2 Infantil 1
        3 Infantil 2
        4 Infantil 3
        
        outros R$ 98,00

        comando:
        python manage.py corrige_cria_parcelas
        '''
        data = date(2018, 12, 20)
        material = CategoriaPagamento.objects.get(id=9)
        contratos = ContratoAluno.objects.filter(ano=2019)
        pagamentos_antes =Pagamento.objects.filter(contrato__ano=2019).count()
        for contrato in contratos:
            pgto = Pagamento()
            pgto.categoria = material
            pgto.titulo = 'Material'
            pgto.data = data
            pgto.efet = False
            pgto.tipo = 1
            pgto.escola = contrato.aluno.escola
            pgto.contrato = contrato
            if contrato.serie.id in [1, 2, 3, 4]:
                pgto.valor = Decimal('165.00')
            else:
                pgto.valor = Decimal('98.00')
            pgto.save()
        pagamentos_depois =Pagamento.objects.filter(contrato__ano=2019).count()
        print('=======================')
        print(pagamentos_antes, pagamentos_depois)



 