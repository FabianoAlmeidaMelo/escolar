# coding: utf-8

from django.db import models
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import(
    AbstractBaseUser,
    BaseUserManager,
)

# from escolar.escolas.models import Escola, Classe

from django.contrib.auth.models import User, Group
from django.conf import settings
from municipios.models import Municipio

SEXO = (
    (1, "M"),
    (2, "F"),
    )


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError(u'Email é obrigatório')
        email = UserManager.normalize_email(email)
        user = self.model(email=email, is_active=True, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Endereco(models.Model):
    '''
    ref #32
    '''
    cep = models.CharField(max_length=9)
    logradouro = models.CharField(max_length=100)
    numero = models.CharField(verbose_name=u'Número', max_length=50)
    complemento = models.CharField(max_length=100, null=True, blank=True)
    bairro = models.CharField(max_length=100)
    municipio = models.ForeignKey(Municipio, null=True, blank=True)
    perfil = models.ForeignKey('Perfil', null=True, blank=True)

    def __str__(self):
        return u"%s - %s" % (self.cep, self.numero)

    class Meta:
        verbose_name = u'Endereço'
        ordering = ('municipio__nome', 'bairro', 'logradouro')

    def __str__(self):
        return '%s - %s' % (self.logradouro, self.municipio)


class Perfil(models.Model):
    '''
    ref #32
    o Perfil estará vinculado ao contrato
    SE tiver email
    a escola pode criar um user a partir do perfil (get_or_create)
    SE for maior de idade:
    cpf será requerido
    '''
    nome = models.CharField(verbose_name=u'Nome', max_length=100)
    escolas = models.ManyToManyField('escolas.Escola')  # escrever a tabela, vai entrar se é aluno, pai, mãe ...
    nascimento = models.DateField(u'Data Nascimento', null=True, blank=True)
    profissao = models.CharField(u'Profissão', max_length=100, null=True, blank=True)
    sexo = models.SmallIntegerField(u'Sexo', null=True, blank=True)
    cpf = models.CharField(verbose_name=u'CPF', max_length=14, null=True, blank=True)
    email = models.EmailField('e-mail', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)

    class Meta:
        verbose_name = u'Perfil Escola'
        verbose_name_plural = u'Perfis Escolas'
        ordering = ('nome',)

    def __str__(self):
        return '%s - %s' % (self.nome, self.cpf)

class User(AbstractBaseUser):
    '''
    '''
    email = models.EmailField('e-mail', unique=True)
    username = models.CharField('username', max_length=100, unique=True)
    nome = models.CharField(verbose_name=u'Nome', max_length=100)
    is_active = models.BooleanField('ativo', default=True,)
    date_joined = models.DateTimeField(
        'data de cadastro', default=timezone.now
        )
    grupos = models.ManyToManyField(Group, through='UserGrupos', related_name='grupos', blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('nome', 'email', )

    class Meta:
        verbose_name = u'Usuário'
        verbose_name_plural = u'Usuários'

    def __str__(self):
        return self.nome

    def can_access_escola(self, escola_pk):
        can_access_escola = self.usergrupos_set.filter( escola__id=escola_pk).count() > 0 or self.is_admin()
        return can_access_escola

    def get_unica_escola(self):
        if self.is_admin:
            return None
        if self.usergrupos_set.all().values_list('escola', flat=True).count() == 1:
            return self.usergrupos_set.all().values_list('escola', flat=True)[0]
        return None

    def is_admin(self):
        return self.grupos.filter(name='Admin').count() > 0

    def is_diretor(self, escola_pk):
        return self.usergrupos_set.filter(grupo__name='Diretor', escola__id=escola_pk).count() == 1

    def is_aluno(self, escola_pk):
        '''
        ref #22
        '''
        return self.usergrupos_set.filter(grupo__name='Aluno', escola__id=escola_pk).count() == 1

    def get_professor_escolas(self):
        '''
        retornar um queryset
        '''
        escolas_ids = self.usergrupos_set.filter(grupo__name='Professor', ativo=True).values_list('escola_id', flat=True)
        return Escola.objects.filter(id__in=escolas_ids)

    def get_diretor_escolas(self):
        '''
        retornar um queryset
        '''
        escolas_ids = self.usergrupos_set.filter(grupo__name='Diretor', ativo=True).values_list('escola_id', flat=True)
        return Escola.objects.filter(id__in=escolas_ids)

    def get_aluno_escolas(self):
        '''
        retornar um queryset
        '''
        escolas_ids = self.usergrupos_set.filter(grupo__name='Aluno', ativo=True).values_list('escola_id', flat=True)
        return Escola.objects.filter(id__in=escolas_ids)

    def get_responsavel_escolas(self):
        '''
        retornar um queryset
        '''
        escolas_ids = self.usergrupos_set.filter(grupo__name='Responsavel', ativo=True).values_list('escola_id', flat=True)
        return Escola.objects.filter(id__in=escolas_ids)

    def get_classe(self, escola):
        '''
        ref #20
        retorna a classe do ano corrente, de uma escola, de um Aluno
        '''
        ano = date.today().year
        classe_aluno = self.classealuno_set.filter(classe__escola=escola, classe__ano=ano).last()
        if classe_aluno:
            return classe_aluno.classe
        return None

    def get_all_classe(self, escola):
        '''
        ref #20
        retorna um histórico de classes de uma
        escola do Aluno
        '''
        return self.classealuno_set.filter(classe__escola=escola).order_by('-classe__ano')

    def get_professor_classes(self, escola):
        '''
        ref #21
        retorna um histórico de classes de uma
        escola do Aluno
        '''
        ano = date.today().year
        classe_ids = self.classeprofessor_set.filter(classe__escola=escola, classe__ano=ano).values_list('classe__id', flat=True)
        return Classe.objects.filter(id__in=classe_ids)

class UserGrupos(models.Model):
    escola = models.ForeignKey('escolas.Escola')
    user = models.ForeignKey(User)
    grupo = models.ForeignKey(Group)
    date_joined = models.DateTimeField(
        'data de cadastro', default=timezone.now
        )
    ativo = models.BooleanField()

    def __str__(self):
        return '%s - %s' % (self.user, self.grupo.name)


class Pais(models.Model):
    '''
    Contry
    fuso horáio, ??? 
    '''
    nome = models.CharField('Nome', max_length=100)
    sigla = models.CharField('Sigla', max_length=3)
    idioma = models.CharField('Idioma', max_length=50, null=True, blank=True)

    def __str__(self):
        return '%s - %s' % (self.nome, self.sigla)

    def get_nacionalidade(self):
        dict_nacionalidade = {'Brasil': 'brasileira'}
        return dict_nacionalidade[self.nome]


class UserAdd(models.Model):
    user_add = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="%(app_label)s_%(class)s_created_by")
    date_add = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class UserUpd(models.Model):
    user_upd = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="%(app_label)s_%(class)s_modified_by")
    date_upd = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class Feriado(models.Model):
    '''
    popula os dados quando tiver clientes
    de um Município, e próximo a liberação de contratos para
    ano seguinte
    popular com get or create no brasil_feriados.py
    Depois que os contratos de um ano estivrem validados, limpar
    os feriados do mesmo ano do BD
    '''
    date = models.DateField('data')
    name = models.CharField(max_length=100)
    type_name = models.CharField(max_length=80)
    type_code = models.SmallIntegerField('tipo')
    uf_ibge_code = models.SmallIntegerField('uf ibge', null=True, blank=True)
    municipio = models.ForeignKey(Municipio, null=True, blank=True)

    def __str__(self):
        return u"%s - %s" % (self.date, self.type_name)

    class Meta:
        verbose_name = u'Feriado'
