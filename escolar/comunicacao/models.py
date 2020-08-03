from django.db import models
from django.conf import settings
# from django.contrib.postgres.fields import JSONField


MENSAGEM_CHOICES = (
    (1, 'cobrança'),
    (2, 'aniversário'),
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

class MensagemDefault(models.Model):
    '''
    # 5
    Permite cada escola criar uma msg
    default para cada situação
    1 por escola 1 para cada tipo
    1 pra acada tipo * tamanho limitado por tipo, ex sms 100 
    Ao cadastrar a Escola já cria uma msg "template"
    e o diretor pode editar a seu critério

    '''
    escola = models.ForeignKey('escolas.Escola')
    tipo = models.SmallIntegerField('Tipo:', choices=MENSAGEM_CHOICES)
    titulo = models.CharField('Título: ', max_length=100)
    cabecalho = models.CharField('Cabeçalho: ', max_length=100)
    corpo = models.TextField('Corpo')
    assinatura = models.CharField('Assinatura:', max_length=300)

    class Meta:
        verbose_name = 'Mensagem Default'
        verbose_name_plural = 'Mensagens Default'
        unique_together = ("escola", "tipo")


class Mensagem(models.Model):
    '''
    #5
    Model para registrar os envios de mensagem de diversos tipos:
    Cobrança, Saudação, Aviso, Conteúdo

    do contrato da para extrair: email, cel, user resp $ , resp didatico
    '''
    escola = models.ForeignKey('escolas.Escola')
    data = models.DateField('data')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    texto = models.TextField('Texto')
    tipo = models.SmallIntegerField(choices=MENSAGEM_CHOICES)
    meio = models.SmallIntegerField(choices=MEIO_CHOICES)
    pessoas = models.ManyToManyField('escolas.Pessoa', through='PessoaMensagem') # 1 msg pode ir para 1 ou 'n' users

    class Meta:
        ordering = ('-data',)

    def __str__(self):
        return 'MSG de :%s ; em: %s' % (self.user.nome, self.data.date())


class PessoaMensagem(models.Model):
    '''
    #5
    registra:
        as pessoas destinatárias das Mensagens
        a data hora que o destinatário abriu a mensagem
    '''
    mensagem = models.ForeignKey(Mensagem)
    pessoa = models.ForeignKey('escolas.Pessoa')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    # por causa do erro na migração
    # acho que é por que esse BD local não tem algumas migraçõs já aplicadas em prod
    contrato_id = models.IntegerField('ID do contrato', null=True, blank=True)
    email = models.EmailField('email do destinatário', max_length=254)
    data = models.DateTimeField('Lida em: ', null=True, blank=True)

    def can_edit(self):
        '''
        SE dos tipos:
        Se Não tem user,
        pode editar
        (4, 'msg_aplicativo'),
        '''
        can_edit = False
        if not self.pk:
            can_edit = True
        elif self.messagem.tipo == 4:
            can_edit = self.user is None
        return can_edit
