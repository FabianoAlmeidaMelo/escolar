# -*- coding: utf-8 -*-
from datetime import date
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from escolar.escolas.models import Escola, Pessoa


class Command(BaseCommand):

    def handle(self, *args, **options):
        '''
        Pessoa.objects.filter(escola=1, nascimento__month=5).count()

        Envia um email com uma lista de
        aniversariantes do dia, para o email principal da escola

        python manage.py alerta_aniversariantes_do_dia
        '''
        hoje = date.today()
        print('\n----\n', hoje)
        escolas = Escola.objects.all()
        for escola in escolas:
            aniversariantes = Pessoa.objects.filter(
                escola=escola,
                nascimento__month=hoje.month,
                nascimento__day=hoje.day)
            if aniversariantes:
                print(aniversariantes.count())
                self.send_email_niver(escola, aniversariantes)

    def send_email_niver(self, escola, aniversariantes):
        nomes = '; \n'.join(aniversariantes.values_list('nome' , flat=True))
        emails = list(escola.usergrupos_set.filter(grupo__name='Diretor').values_list('user__email', flat=True))
        msg = 'Essas pessoas fazem aniversário hoje:'
        url = 'https://smartiscool.online/escola/%s/aniversariantes_list/' % escola.id
        assinatura= 'Você pode lhes enviar um email\n %s' % url
        if emails:
            mensagem = 'Aniversariasntes de Hoje'
            mensagem += '\n\n%s' % msg
            mensagem += '\n\n%s' % nomes
            mensagem += '\n\n%s' % assinatura

            
            send_mail(
                'Feliz Aniversário',
                mensagem,
                settings.DEFAULT_FROM_EMAIL,
                emails,
                fail_silently=False
            )
            return True

 