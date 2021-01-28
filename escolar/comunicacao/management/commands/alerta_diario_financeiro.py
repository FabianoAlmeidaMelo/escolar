# -*- coding: utf-8 -*-
from datetime import date
from django.db.models import BooleanField, Case, Value, When, Q, Sum
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from escolar.escolas.models import Escola
from escolar.financeiro.forms import (
    ANO_CORRENTE,
    MES_CORRNETE,
)

class Command(BaseCommand):
    """ref #14 github
    cat /etc/cron.d/helper
    sudo nano /etc/cron.d/helper
    08 01 * * * ubuntu /var/www/projetos/escolar/escolar/scripts/alerta_diario_financeiro.sh 2>&1 > /tmp/email_nivres_py.txt

    # torna o arquivo executável:
    chmod +x /var/www/projetos/escolar/escolar/escolar/scripts/

    sudo systemctl status cron
    sudo systemctl restart cron
    """
    pagamentos = apps.get_model('financeiro', 'Pagamento')
    data_ini = date(ANO_CORRENTE, MES_CORRNETE, 1)
    hoje = date.today()

    emails_dict = {1: ['travelho.castro@gmail.com'],
    2: [],
    3: [],
    4: []
    }

    def handle(self, *args, **options):
        '''
        Pessoa.objects.filter(escola=1, nascimento__month=5).count()

        Envia um email com uma lista de
        aniversariantes do dia, para o email principal da escola

        python manage.py alerta_diario_financeiro
        '''

        escolas = Escola.objects.all()

        for escola in escolas:
            pgtos_qs = self.check_pagamentos(escola)
            if pgtos_qs:
                self.send_email_pgto_pendentes(escola, pgtos_qs)
            print("=============================================")
            print(escola.nome)
            msg = 'Envio de emails Pgtos pendentes do dia: %s : %s' % (
                self.hoje, pgtos_qs.count()
            )
            print(msg)

    def check_pagamentos(self, escola):
        
        pgtos_qs = self.pagamentos.objects.filter(
            escola=escola,
            data__gte=self.data_ini,
            data__lte=self.hoje
        ).annotate(
            invalido=Case(
                When(
                    contrato__isnull=False,
                    contrato__rescindido=True,
                    efet=False,
                    then=Value(True)
                ), output_field=BooleanField()
            )
        )
        pgtos_qs = pgtos_qs.filter(invalido=None, efet=False)

        return pgtos_qs

    def send_email_pgto_pendentes(self, escola, pgtos_qs):
        dividas = ''' '''
        recebimentos = ''' '''
        receb_qs = pgtos_qs.filter(tipo=1, efet=False)
        if receb_qs:
            for p in receb_qs:
                recebimentos += '%s, R$ %s; \n' % (str(p.data_pag.date()), str(p.valor))
        else:
            recebimentos = 'Não há recebimentos em aberto'

        divida_qs = pgtos_qs.filter(tipo=2, efet=False)
        if divida_qs:
            for p in divida_qs:
                dividas += '%s, R$ %s; \n' % (str(p.data_pag.date()), str(p.valor))
        else:
            dividas = 'Não há pagamentos em aberto'

        emails = self.emails_dict.get(escola.id, [])
        msg = 'Esses pagamentos do mês corrente ainda estão em aberto.' 
        msg += '\nApurados até a data de hoje: %s' % self.hoje
        url = 'https://smartiscool.online/%s/' % escola.id
        assinatura= 'Pode conferir mais detalhes em:\n%s' % url
        if emails:

            mensagem = '\n\n%s' % msg
            mensagem += '\nPagamentos Pendentes:' 
            mensagem += '\n\n%s' % dividas
            mensagem += '\nRecebimentos Pendentes:'
            mensagem += '\n\n%s' % recebimentos
            mensagem += '\n\n%s' % assinatura
            
            send_mail(
                'Pendencias no financeiro /%s' % escola.nome,
                mensagem,
                settings.DEFAULT_FROM_EMAIL,
                emails,
                fail_silently=False
            )
            return True
 