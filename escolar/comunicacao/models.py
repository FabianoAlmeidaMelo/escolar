from django.db import models

MENSAGEM_CHOICES = (
    (1, 'cobrança'),
    (2, 'saudação'),
    (3, 'avisos'),
    (4, 'conteúdo'),
    (5, 'outros'),
)

MEIO_CHOICES = (
    (1, 'email'),
    (2, 'sms'),
    (3, 'whatsApp'),
    (4, 'msg_aplicativo'),
    (5, 'carta'),
    (6, 'telefone'),
)


class ControleMensgem(models.Model):
    '''
    #5
    Model para controlar os envios de mensagem de diversos tipos:
    Cobrança, Saudação, Aviso, Conteúdo

    do contrato da para extrair: email, cel, user resp $ , resp didatico
    '''
    escola = models.ForeignKey('escolas.Escola')
    contrato = models.ForeignKey('financeiro.Contrato', null=True, blank=True)
    date = models.DateField('data')
    user = models.ForeignKey('core.User') # enviou
    resumo = models.TextField() # o que foi enviado para quem: 5 parcelas em atraso
    tipo = models.SmallIntegerField(choices=MENSAGEM_CHOICES)
    meio = models.SmallIntegerField(choices=MEIO_CHOICES)
