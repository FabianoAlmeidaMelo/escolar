from django.db import models
from municipios.models import Municipio
from escolar.core.models import User


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

class Escola(models.Model):
    '''
    se fosse o bitbucket seria um 'Projeto'?
    '''
    nome=models.CharField(max_length=200)
    endereco=models.CharField(max_length=200)
    numero=models.CharField(max_length=10)
    telefone = models.CharField(max_length=14, null=True, blank=True)
    complemento = models.CharField(max_length=100, null=True, blank=True)
    bairro = models.CharField(max_length=100)
    municipio = models.ForeignKey(Municipio)
    created_at = models.DateTimeField('data de cadastro', auto_now_add=True)


class Equipe(models.Model):
    '''
    m2m EscolaUser
    Imagino um user diretor, adicionando outros users
    do time da escola: professores, secretários, ...
    mas os Alunos e responsáveis, creio que entrarão no
    sistema por Upload de planilha
    '''
    escola = models.ForeignKey(Escola)
    user = models.ForeignKey(User)
    grupo = models.SmallIntegerField('Grupo', choices=GRUPO) # like a User Group / bitibucket
    ativo = models.BooleanField('Ativo', default=True) # Não remove da equipe, ativa ou inativa


class Classe(models.Model):
    escola = models.ForeignKey(Escola)
    curso = models.CharField(max_length=20) # ex: 5º ano A
    professor = models.ManyToManyField(User, related_name='professor')  # m2m ?? embora até o 5º ano seja 1 prof
    turma = models.ManyToManyField(User, related_name='turma')
    periodo = models.SmallIntegerField(choices=PERIODO, null=True, blank=True)





