# coding: utf-8

from django.db import models
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import(
    AbstractBaseUser,
    BaseUserManager,
)

from escolar.escolas.models import Escola

from django.contrib.auth.models import User, Group

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


class User(AbstractBaseUser):
    '''
    '''
    email = models.EmailField('e-mail', unique=True)
    nome = models.CharField(verbose_name=u'Nome', max_length=100)
    is_active = models.BooleanField('ativo', default=True,)
    # is_superuser = models.BooleanField(default=False)
    # is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(
        'data de cadastro', default=timezone.now
        )
    # nascimento = models.DateField(u'Data Nascimento', null=True, blank=True)
    # profissao = models.CharField(
        # u'Profissão', max_length=100, null=True, blank=True
        # )
    # sexo = models.IntegerField(u'Sexo', choices=SEXO, null=True, blank=True)
    grupos = models.ManyToManyField(Group, through='UserGrupos', related_name='grupos', blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('nome', )

    class Meta:
        verbose_name = u'Usuário'
        verbose_name_plural = u'Usuários'

    def __str__(self):
        return self.nome

    def is_admin(self):
        return self.grupos.filter(name='Admin').count() == 1

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
        return self.classeprofessor_set.filter(classe__escola=escola, classe__ano=ano)

class UserGrupos(models.Model):
    escola = models.ForeignKey(Escola)
    user = models.ForeignKey(User)
    grupo = models.ForeignKey(Group)
    date_joined = models.DateTimeField(
        'data de cadastro', default=timezone.now
        )
    ativo = models.BooleanField()

    def __unicode__(self):
        return '%s - %s' % (self.user, self.grupo.name)
