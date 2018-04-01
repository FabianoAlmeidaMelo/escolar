# -*- coding: utf-8 -*-
from django.core.mail import send_mail
from datetime import datetime
from escolar.settings import DEFAULT_FROM_EMAIL


def send_mail_teste():
    '''
    Ex: from escolar.utils.testar_envio_de_email import *
    '''

    emails = [u'falmeidamelo@uol.com.br']

    mensagem = u'Teste de envio de emails do control H - %s' % datetime.today()

    if emails:
        send_mail(
            u'Teste de envio/ Smart Is Cool',
            mensagem,
            DEFAULT_FROM_EMAIL,
            emails,
            fail_silently=False,
        )
