# -*- coding: utf-8 -*-
from datetime import date
from django.db.models import Q
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from escolar.comunicacao.utils.aws_ses import send_email
from escolar.escolas.models import Escola, Pessoa


class Command(BaseCommand):
    """ref #30
    cat /etc/cron.d/helper
    sudo nano /etc/cron.d/helper
    10 01 * * * ubuntu /var/www/projetos/escolar/escolar/scripts/alerta_aniversariantes_do_dia.sh 2>&1 > /tmp/email_nivres_py.txt

    # torna o arquivo executável:
    chmod +x /var/www/projetos/escolar/escolar/escolar/scripts/

    sudo systemctl status cron
    sudo systemctl restart cron
    """
    contratos = apps.get_model('financeiro', 'ContratoAluno')
    ano = date.today().year

    def handle(self, *args, **options):
        '''
        Pessoa.objects.filter(escola=1, nascimento__month=5).count()

        Envia um email com uma lista de
        aniversariantes do dia, para o email principal da escola

        python manage.py alerta_aniversariantes_do_dia
        '''
        hoje = date.today()
        escolas = Escola.objects.all()

        for escola in escolas:
            nivers = self.check_nivers(escola, hoje)
            if nivers:
                self.send_email_niver(escola, nivers)
            print("=============================================")
            print(escola.nome)
            msg = 'Envio de emails de Nivers do dia: %s Nivers: %s' % (
                hoje, nivers.count()
            )
            print(msg)

    def check_nivers(self, escola, hoje):
        q = Q(escola=escola)
        pessoas = Pessoa.objects.filter(escola=escola)
        alunos_ativos_ids = self.contratos.objects.filter(
            ano=self.ano,
            aluno__escola=escola).values_list('aluno__id', flat=True)
        resp_ativos_ids = self.contratos.objects.filter(
            ano=self.ano,
            aluno__escola=escola).values_list('responsavel__id', flat=True)
        q = q & Q(id__in=alunos_ativos_ids) | Q(id__in=resp_ativos_ids)
        pessoas = pessoas.filter(q)
        nivers = pessoas.filter(
            nascimento__month=hoje.month,
            nascimento__day=hoje.day).filter(q)
        return nivers

    def send_email_niver(self, escola, aniversariantes):
        nomes = ''' '''
        for p in aniversariantes:
            nomes += '%s, %s, %s, %s; \n' % (p.nome, p.get_modelo_filho(), p.email or'-', p.celular or'-')

        emails = list(escola.usergrupos_set.filter(
            grupo__name='Diretor').values_list('user__email', flat=True))

        msg = 'Essas pessoas tem contrato em %s com sua escola e fazem aniversário hoje:' % self.ano
        url = 'https://smartiscool.online/escola/%s/aniversariantes_list/' % escola.id
        assinatura= 'Você pode lhes enviar um email\n%s' % url
        if emails:
            mensagem = 'Aniversariasntes de Hoje'
            mensagem += '\n\n%s' % msg
            mensagem += '\n\n%s' % nomes
            mensagem += '\n\n%s' % assinatura
            txt_message = mensagem
            html_message = """<p>{msg}</p>""".format(msg=mensagem)

            for recipient in emails:
                send_email(
                    recipient,
                    'Aniversariantes de Hoje',
                    txt_message,
                    html_message,
                    escola.nome
                )
                return True

 