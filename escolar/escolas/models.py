# coding: utf-8
import os
from django.db import models
from django.utils import timezone
# from django.contrib.auth.models import User
from municipios.models import Municipio
from datetime import date
from django.conf import settings

from escolar.core.models import UserAdd, UserUpd

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
    Escola que fez o upload do arquivo
    file will be uploaded to MEDIA_ROOT/conta_<id>/<filename>
    '''
    return 'escola_{0}/{1}'.format(instance.nome, logo)

class Escola(models.Model):
    '''
    '''
    pais = models.ForeignKey('core.Pais')  # País, Country
    nome = models.CharField('nome', max_length=200)
    razao_social = models.CharField('razão social', max_length=200)
    cnpj = models.CharField('cnpj', max_length=14)
    municipio = models.ForeignKey(Municipio)
    endereco = models.CharField('endereço', max_length=200)
    numero = models.CharField('número', max_length=10)
    telefone = models.CharField('telefone', max_length=14, null=True, blank=True)
    celular = models.CharField('celular', max_length=14, null=True, blank=True)
    complemento = models.CharField('comnplemento', max_length=100, null=True, blank=True)
    bairro = models.CharField('bairro', max_length=100)
    created_at = models.DateTimeField('data de cadastro', auto_now_add=True)
    slug = models.CharField('slug', max_length=50, null=True)
    logo = models.ImageField(upload_to=escola_directory_path, null=True, blank=True)
    site = models.URLField('website', blank=True, null=True)
    description = models.TextField('descrição', blank=True, null=True)
    publica = models.BooleanField(u'Escola pública', default=False)
    cursos = models.ManyToManyField('Curso')

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

    def get_docs_name(self):

        return os.path.basename(self.logo.name)


class Curso(models.Model):
    '''
    cursos básicos, default para todas escolas,
    balizados pela Lei e Mec, criados geridos pelo admin.
    cursos customizados e ou livres: criados e gerenciados por escola
    Berçário  0 A 2 ANOS
    '''
    nome = models.CharField(max_length=100)
    # escola = models.ForeignKey(Escola, null=True, blank=True)

    def __str__(self):
        return self.nome

class Serie(models.Model):
    '''
    séries default, para todos os cursos e
    possibilidade de Escola criar uma 'série' especial
    '''
    curso = models.ForeignKey(Curso)
    serie = models.CharField(max_length=30)

    def __str__(self):
        return "%s - %s" % (self.serie, self.curso.nome)
    
    class Meta:
        verbose_name = 'série'
        verbose_name_plural = 'séries'
        ordering = ('id',)

def escola_aluno_directory_path(instance, documento):
    '''
    Escola que fez o upload do arquivo
    file will be uploaded to MEDIA_ROOT/escola_<id>/<aluno_nome>
    '''
    escola = instance.escola.nome
    aluno = instance.nome
    return 'escola_{0}/secretaria/aluno_{1}/{2}'.format(escola, aluno, documento)


# class Pessoa(UserAdd, UserUpd):
#     # comum
#     celular = models.CharField(max_length=11, null=True, blank=True)
#     cpf = models.CharField(verbose_name=u'CPF', max_length=14, null=True, blank=True)
#     documento = models.FileField('RG e ou CPF', upload_to=escola_aluno_directory_path, null=True, blank=True)
#     email = models.EmailField('e-mail', null=True, blank=True)
#     endereco = models.ForeignKey('core.Endereco', null=True, blank=True)
#     escola = models.ForeignKey(Escola)
#     nacionalidade = models.CharField(max_length=50)
#     nascimento = models.DateField(u'Data Nascimento', null=True, blank=True)
#     natural_municipio = models.ForeignKey(Municipio, null=True, blank=True)
#     nome = models.CharField(max_length=100)
#     profissao = models.CharField(u'Profissão', max_length=100, null=True, blank=True)
#     rg = models.CharField(verbose_name=u'RG', max_length=14, null=True, blank=True)
#     sexo = models.SmallIntegerField(u'Sexo')
#     telefone = models.CharField(max_length=11, null=True, blank=True)
#     user = models.ForeignKey('core.User', null=True, blank=True)


class Aluno(UserAdd, UserUpd):
    '''
    ref #33
    Aluno tem Ficha de Matrícula, fica arquivada na Escola
    não está ao 'alcance' do aluno e ou pais para edição
    é um doc da Escola, diferente do Perfil que "é" do User
    Nesse caso, acho que vou optar por ligar o user
    no aluno e membro, assim p último é o perfil
    '''
    # pessoa = models.OneToOneField(Pessoa, null=True)

    celular = models.CharField(max_length=11, null=True, blank=True)
    cpf = models.CharField(verbose_name=u'CPF', max_length=14, null=True, blank=True)
    documento = models.FileField('RG e ou CPF', upload_to=escola_aluno_directory_path, null=True, blank=True)
    email = models.EmailField('e-mail', null=True, blank=True)
    endereco = models.ForeignKey('core.Endereco', null=True, blank=True)
    escola = models.ForeignKey(Escola)
    nacionalidade = models.CharField(max_length=50)
    nascimento = models.DateField(u'Data Nascimento', null=True, blank=True)
    natural_municipio = models.ForeignKey(Municipio, null=True, blank=True)
    nome = models.CharField(max_length=100)
    profissao = models.CharField(u'Profissão', max_length=100, null=True, blank=True)
    rg = models.CharField(verbose_name=u'RG', max_length=14, null=True, blank=True)
    sexo = models.SmallIntegerField(u'Sexo')
    telefone = models.CharField(max_length=11, null=True, blank=True)
    user = models.ForeignKey('core.User', null=True, blank=True)
    
    ano = models.SmallIntegerField(default=ano_corrente)
    curso = models.ForeignKey('Curso', null=True, blank=True)
    foto = models.ImageField('Foto', upload_to=escola_aluno_directory_path, null=True, blank=True)
    observacao = models.CharField(max_length=200, null=True, blank=True)
    ra = models.CharField('RA', max_length=20, null=True, blank=True)


    class Meta:
        verbose_name = 'aluno'
        verbose_name_plural = 'alunos'
        ordering = ('nome',)

    def __str__(self):
        return self.nome


    def get_docs_name(self):
        return os.path.basename(self.documento.name)

    def list_pendencias_contrato(self):
        pendencias = []
        if self.count_responsavel_financeiro() == 0:
            pendencias.append('Necessário definir um Responsável Financeiro no cadastro dos Familiares')
        if not self.curso:
            pendencias.append('Necessário definir o Curso no cadastro do Aluno')
        return pendencias

    def count_responsavel_financeiro(self):
        return self.responsavel_set.filter(responsavel_financeiro=True).count()

    def get_responsavel_financeiro(self):
        first_resp = self.responsavel_set.filter(responsavel_financeiro=True).first()
        if first_resp:
            return first_resp.membro

    def get_responsavel_pedagogico(self):
        first_resp = self.responsavel_set.filter(responsavel_pedagogico=True).first()
        if first_resp:
            return first_resp.membro

    def get_sexo_display(self):
        sexo = {1: 'masculino', 2: 'feminino'}
        return sexo[self.sexo]

    def get_curso(self):
        if self.contrato_aluno.count():
            return self.contrato_aluno.filter(ano=ano_corrente)[0].curso

    def get_serie(self):
        if self.contrato_aluno.count():
            return self.contrato_aluno.filter(ano=ano_corrente)[0].serie

    def get_data_matricula(self):
        if self.contrato_aluno.count():
            return self.contrato_aluno.filter(ano=ano_corrente)[0].data_assinatura


class Responsavel(models.Model):
    aluno = models.ForeignKey(Aluno)
    membro = models.ForeignKey('MembroFamilia')
    parentesco = models.CharField(max_length=100, null=True, blank=True)
    responsavel_financeiro = models.BooleanField(default=False)
    responsavel_pedagogico = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Responsável'
        verbose_name_plural = 'Responsáveis'

    def __str__(self):
        return '%s' % self.membro.nome

def escola_aluno_parente_directory_path(instance, arquivo):
    '''
    Escola que fez o upload do arquivo
    file will be uploaded to MEDIA_ROOT/escola_<id>/<aluno_nome>
    '''
    escola = instance.responsavel_set.filter(aluno__ano=2018).order_by('aluno_id').first().aluno.escola.nome
    aluno = instance.responsavel_set.filter(aluno__ano=2018).order_by('aluno_id').first().aluno.nome
    return 'escola_{0}/secretaria/aluno_{1}/responsavel/{2}'.format(escola, aluno, arquivo)


class MembroFamilia(UserAdd, UserUpd):
    '''
    ref #33
    Aluno tem Ficha de Matrícula, fica arquivada na Escola
    não está ao 'alcance' do aluno e ou pais para edição
    é um doc da Escola
    '''
    # pessoa = models.OneToOneField(Pessoa, null=True)

    celular = models.CharField(max_length=11, null=True, blank=True)
    cpf = models.CharField(verbose_name=u'CPF', max_length=14, null=True, blank=True)
    documento = models.FileField('RG e ou CPF', upload_to=escola_aluno_parente_directory_path, null=True, blank=True)
    email = models.EmailField('e-mail', null=True, blank=True)
    nascimento = models.DateField(u'Data Nascimento', null=True, blank=True)
    nome = models.CharField(max_length=100)
    profissao = models.CharField(u'Profissão', max_length=100, null=True, blank=True)
    rg = models.CharField(verbose_name=u'RG', max_length=14, null=True, blank=True)
    sexo = models.SmallIntegerField(u'Sexo')
    telefone = models.CharField(max_length=11, null=True, blank=True)
    user = models.ForeignKey('core.User', null=True, blank=True)
    
    # comrecial
    empresa = models.CharField(max_length=100, null=True, blank=True)
    obs_empresa = models.CharField(max_length=100, null=True, blank=True)
    parentesco = models.CharField(max_length=100)
    responsavel_financeiro = models.BooleanField(default=False)
    responsavel_pedagogico = models.BooleanField(default=False)
    telefone_empresa = models.CharField(max_length=11, null=True, blank=True)

    class Meta:
        verbose_name = 'Membro da Família'
        verbose_name_plural = 'Membros da Família'
        ordering = ('nome',)

    def get_sexo_display(self):
        sexo = {1: 'masculino', 2: 'feminino'}
        return sexo[self.sexo]

    def __str__(self):
        return self.nome

    def get_docs_name(self):

        return os.path.basename(self.documento.name)


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
    # ativo = models.BooleanField('Autorizado', default=False)

    def __str__ (self):
        return self.nome


class AutorizadoAluno(models.Model):
    '''
    #22
    pessoas autorizadas a buscar alunos na escola
    '''
    escola = models.ForeignKey(Escola)
    aluno = models.ForeignKey(Aluno)
    autorizado = models.ForeignKey(Autorizado)
    responsavel = models.ForeignKey('core.User')
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