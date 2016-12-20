from django.db import models
from django.contrib.auth.models import Group
from municipios.models import Municipio
from escolar.core.models import User
from django.conf import settings

PERIODO = (
    (1, 'Manhã'),
    (2, 'Tarde'),
    (3, 'Noite'),
)


GRUPO = (
    (1, 'Direção'),
    (2, 'Professor'),
    (3, 'Aluno'),
    (4, 'Responsável'),
)

ANO = (
    (2016, 2016),
    (2017, 2017),
    (2018, 2018),
)


class Escola(models.Model):
    '''
    '''
    nome = models.CharField('nome', max_length=200)
    endereco = models.CharField('endereço', max_length=200)
    numero = models.CharField('número', max_length=10)
    telefone = models.CharField('telefone', max_length=14, null=True, blank=True)
    complemento = models.CharField('comnplemento', max_length=100, null=True, blank=True)
    bairro = models.CharField('bairro', max_length=100)
    # municipio = models.ForeignKey(Municipio)
    created_at = models.DateTimeField('data de cadastro', auto_now_add=True)
    slug = models.CharField('slug', max_length=50, null=True)
    # logo = models.URLField(upload_to='%s/escolas/logotipo/' % (settings.UPLOAD_PATH), max_length=300,  blank=True, null=True)
    site = models.URLField('website', blank=True, null=True)
    description = models.TextField('descrição', blank=True, null=True)

    class Meta:
        verbose_name = 'escola'
        verbose_name_plural = 'escolas'
        ordering = ('nome',)

    def __str__(self):
        return self.nome


    def get_status(self):
        '''
        TODO:
        será analizado por período da assinatura
        se estiver válido, retorna True
        '''
        return True

class Grupo(Group):
    nome = models.CharField('Nome', max_length=80)
    escola = models.ForeignKey(Escola)

    class Meta:
        unique_together = ('nome', 'escola')
        verbose_name = 'grupo'
        verbose_name_plural = 'grupos'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = '%s_%s' % (self.nome, self.escola.nome)
        super(Grupo, self).save(*args, **kwargs)


class GrupoUser(models.Model):
    grupo = models.ForeignKey(Grupo)
    user = models.ForeignKey(User)
    # ativo = models.BooleanField()


    def __str__(self):
        return '%s , %s' % (self.user.nome, self.grupo.name,)


# class Turma(models.Model):
#     escola = models.ForeignKey(Escola)
#     ano = models.DateField('Ano')
#     curso = models.ForeignKey('Cusro')
#     professor = models.ManyToManyField(User, related_name='professor')
#     aluno = models.ManyToManyField(Aluno)


# class Classe(models.Model):
#     escola = models.ForeignKey(Escola)
#     ano = models.SmallIntegerField('Ano', choices=ANO)  # 2017
#     curso = models.CharField(max_length=20) # ex: 5º ano A
#     professor = models.ManyToManyField(Professor, related_name='professor')  # m2m ?? embora até o 5º ano seja 1 prof
#     turma = models.ManyToManyField(Aluno, related_name='turma')
#     periodo = models.SmallIntegerField(choices=PERIODO, null=True, blank=True)

    # def __unicode__(self):
    #     return "%s - %s "% (self.curso, str(self.ano))

# class Agenda(models.Model):
#     aluno = models.ForeignKey(Aluno)



