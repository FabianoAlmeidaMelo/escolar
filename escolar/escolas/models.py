# coding: utf-8
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# from municipios.models import Municipio
from datetime import date
from django.conf import settings

PERIODO = (
    (1, u'Manhã'),
    (2, u'Tarde'),
    (3, u'Noite'),
)

ano_corrente = date.today().year
ano_seguinte = ano_corrente + 1
ano_anterior = ano_corrente - 1
 
ANO = (
    (None, '--'),
    (ano_anterior, ano_anterior),
    (ano_corrente, ano_corrente),
    (ano_seguinte, ano_seguinte),
)

meses = list(range(1,13))
MESES = tuple(zip(meses, meses))

def escola_directory_path(instance, logo):
    '''
    conta que fez o upload do arquivo
    file will be uploaded to MEDIA_ROOT/conta_<id>/<filename>
    '''
    return 'escola_{0}/{1}'.format(instance.nome, logo)

class Escola(models.Model):
    '''
    '''
    pais = models.ForeignKey('core.Pais')
    nome = models.CharField('nome', max_length=200)
    endereco = models.CharField('endereço', max_length=200)
    numero = models.CharField('número', max_length=10)
    telefone = models.CharField('telefone', max_length=14, null=True, blank=True)
    celular = models.CharField('celular', max_length=14, null=True, blank=True)
    complemento = models.CharField('comnplemento', max_length=100, null=True, blank=True)
    bairro = models.CharField('bairro', max_length=100)
    # municipio = models.ForeignKey(Municipio)
    created_at = models.DateTimeField('data de cadastro', auto_now_add=True)
    slug = models.CharField('slug', max_length=50, null=True)
    logo = models.ImageField(upload_to=escola_directory_path, null=True, blank=True)
    site = models.URLField('website', blank=True, null=True)
    description = models.TextField('descrição', blank=True, null=True)
    publica = models.BooleanField(u'Escola pública', default=False)

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

class Classe(models.Model):
    escola = models.ForeignKey(Escola)
    ano = models.SmallIntegerField('Ano', choices=ANO)
    curso = models.CharField(max_length=50) # ex: 5º ano A; 5º ano ensino fundamental B; ...
    periodo = models.SmallIntegerField(choices=PERIODO, null=True, blank=True)

    class Meta:
        ordering = ['-ano']

    def __str__(self):
        return "%s - %s "% (self.curso, str(self.ano))

class ClasseAluno(models.Model):
    classe = models.ForeignKey(Classe)
    aluno = models.ForeignKey('core.User')

    class Meta:
        unique_together = ("classe", "aluno")
        ordering = ['aluno__nome']

    def __str__(self):
        return '%s-%s' % (self.classe, self.aluno)

class ClasseProfessor(models.Model):
    classe = models.ForeignKey(Classe)
    professor = models.ForeignKey('core.User')
    materia = models.CharField(max_length=80)

    class Meta:
        unique_together = ("classe", "professor", "materia")

    def __str__(self):
        return '%s-%s: %s' % (self.classe, self.professor, self.materia)


class Autorizado(models.Model):
    '''
    #22
    pessoas autorizadas a buscar alunos na escola
    '''
    nome = models.CharField('Nome', max_length=200)
    email = models.EmailField('email', max_length=200, unique=True)
    celular = models.CharField('celular', max_length=14)
    documento = models.CharField(max_length=25, unique=True)
    # foto = models.ImageField(upload_to='%s' % (settings.MEDIA_URL), max_length=300, blank=True, null=True)

    def __str__ (self):
        return self.nome


class AutorizadoAluno(models.Model):
    '''
    #22
    pessoas autorizadas a buscar alunos na escola
    '''
    escola = models.ForeignKey(Escola)
    aluno = models.ForeignKey('core.User', related_name='autorizados_aluno')
    autorizado = models.ForeignKey(Autorizado)
    responsavel = models.ForeignKey('core.User', related_name='responsavel')
    data = models.DateTimeField('data de cadastro', default=timezone.now)
    status = models.BooleanField('Ativo', default=False)

    def __str__ (self):
        return "Aluno: %s; Autorizado %s; Status: %s" % (self.aluno, self.autorizado, self.status)


# class ResponsavelAluno(models.Model):
#     '''
#     #23
#     users responsáveis pelos alunos perante a escola
#     Pais de alunos, quem assina o contrato.
#     '''
#     escola = models.ForeignKey(Escola)
#     aluno = models.ForeignKey('core.User', related_name='responseveis_aluno')
#     responsavel = models.ForeignKey('core.User', related_name='responsavel_pelo_aluno')
#     data = models.DateTimeField('data de cadastro', default=timezone.now)

#     def __str__ (self):
#         return "Aluno: %s; Responsavel: %s" % (self.aluno, self.responsavel)