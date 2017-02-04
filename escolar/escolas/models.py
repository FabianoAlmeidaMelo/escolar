from django.db import models
from django.contrib.auth.models import User
from municipios.models import Municipio
from datetime import date
from django.conf import settings

PERIODO = (
    (1, 'Manhã'),
    (2, 'Tarde'),
    (3, 'Noite'),
)

ano_corrente = date.today().year
ano_seguinte = ano_corrente + 1
ano_anterior = ano_corrente - 1
 
ANO = (
    (ano_anterior, ano_anterior),
    (ano_corrente, ano_corrente),
    (ano_seguinte, ano_seguinte),
)


class Escola(models.Model):
    '''
    '''
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
    logo = models.ImageField(upload_to='%s' % (settings.MEDIA_URL), max_length=300, blank=True, null=True)
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

    def __str__(self):
        return '%s-%s' % (clase, aluno)

class ClasseProfessor(models.Model):
    classe = models.ForeignKey(Classe)
    professor = models.ForeignKey('core.User')
    materia = models.CharField(max_length=80)

    class Meta:
        unique_together = ("classe", "professor", "materia")

    def __str__(self):
        return '%s-%s: %s' % (clase, professor, materia)


# class Autorizados(models.Model):
#     '''
#     pessoas autorizadas a buscar alunos na escola
#     '''
#     nome = models.CharField('Nome', max_length=200)
#     email = models.EmailField('email', max_length=200)
#     celular = models.CharField('celular', max_length=14)
#     # alunos = models.ManyToManyField(Aluno)
#     escola = models.ForeignKey(Escola)
#     foto = models.ImageField(upload_to='%s' % (settings.MEDIA_URL), max_length=300, blank=True, null=True)
#     status = models.BooleanField('Ativo' )

#     def __str__ (self):
#         return self.nome



