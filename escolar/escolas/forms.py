# coding: utf-8
from datetime import date
from decimal import Decimal
from django.apps import apps
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.db.models import Q
from django import forms
from municipios.widgets import SelectMunicipioWidget
from django.db.models.functions import Extract

from localbr.formfields import BRCPFField, BRCNPJField, BRPhoneNumberField

from escolar.comunicacao.models import MensagemDefault
from escolar.core.widgets import DateTimePicker
from escolar.financeiro.models import ParametrosContrato
from escolar.escolas.models import (
    Aluno,
    ANO,
    Autorizado,
    AutorizadoAluno,
    Classe,
    ClasseAluno,
    ClasseProfessor,
    Curso,
    Escola,
    MembroFamilia,
    Pessoa,
    Responsavel,
    Serie,
)

from escolar.core.models import User, UserGrupos

 
ANO = (
    (None, '--'),
    ('2016', '2016'),
    ('2017', '2017'),
    ('2018', '2018'),
    ('2019', '2019'),
    ('2020', '2020'),
    ('2021', '2021'),
)

hoje = date.today()
ano_corrente = hoje.year

SEXO_CHOICES = (
    (None, '---'),
    (1, 'Masculino'),
    (2, 'Feminino'),
)


COM_SEM_CONTRATO =( 
    (1,'Com Contrato'),
    (2,'Sem Contrato'),
)


CHOICE_MONTH = (
    (None, '--'),
    (1, 'Jan'),
    (2, 'Fev'),
    (3, 'Mar'),
    (4, 'Abr'),
    (5, 'Mai'),
    (6, 'Jun'),
    (7, 'Jul'),
    (8, 'Ago'),
    (9, 'Set'),
    (10, 'Out'),
    (11, 'Nov'),
    (12, 'Dez'),
)

INITIAL_MONTH = date.today().month

def set_only_number(txt):
    txt = str(txt)
    especiais = "_-./;^;ç=*&%''$#@!"
    only_numeros = ''
    for c in txt:
        if c not in especiais:
            only_numeros += c
    return only_numeros



class AutorizadoForm(forms.ModelForm):
    '''#22'''
    documento = BRCPFField(required=True, always_return_formated=True, return_format=u'%s%s%s%s', help_text='Somente números')

    def __init__(self, *args, **kwargs):
        self.escola = kwargs.pop('escola', None)
        self.aluno = kwargs.pop('aluno', None)
        self.responsavel = kwargs.pop('responsavel', None)
        super(AutorizadoForm, self).__init__(*args, **kwargs)

        self.fields['documento'].label = 'CPF'

    def save(self, *args, **kwargs):
        instance = self.instance
        autorizado, create = Autorizado.objects.update_or_create(documento=instance.documento,
                                                                 defaults={'email': instance.email,
                                                                           'nome': instance.nome, 
                                                                           'celular': instance.celular,
                                                                           'telefone': instance.telefone})
        
        autorizado_aluno, created = AutorizadoAluno.objects.update_or_create(escola=self.escola,
                                                                             aluno=self.aluno,
                                                                             autorizado=autorizado,
                                                                             defaults={'responsavel': self.responsavel,
                                                                                       'status': True})
        instance = autorizado
        instance.save()
        return instance


    class Meta:
        model = Autorizado
        fields = ('nome', 'email', 'celular', 'telefone', 'documento') 

class EscolaForm(forms.ModelForm):
    logo = forms.ImageField(label='Logo', required=False)
    cursos = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                            queryset=Curso.objects.all())
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EscolaForm, self).__init__(*args, **kwargs)
        if not self.user.is_admin():
            self.fields['publica'].widget = forms.HiddenInput()

    class Meta:
        model = Escola
        widgets = {'municipio': SelectMunicipioWidget}
        exclude = ('created_at',)

    def save(self, *args, **kwargs):
        instance = super(EscolaForm, self).save(*args, **kwargs)
        instance.save()
        if not instance.parametroscontrato_set.count() and instance.publica is False:
            ParametrosContrato.objects.get_or_create(escola=instance,
                                                     defaults={'ano':ano_corrente,
                                                               'matricula_valor': Decimal('0'),
                                                               'vencimento':10})
        return instance


class AlunoForm(forms.ModelForm):
    ra = forms.CharField(label='RA', required=False)
    cpf = BRCPFField(required=False, always_return_formated=True, return_format=u'%s%s%s%s', help_text='Somente números')
    sexo = forms.ChoiceField(label= 'Sexo',choices=SEXO_CHOICES)
    nascimento = forms.DateField(label='Data Nascimento', required=False, widget=DateTimePicker(options={"format": "DD/MM/YYYY", "pickTime": False}))

    def __init__(self, *args, **kwargs):
        self.escola = kwargs.pop('escola', None)
        self.user = kwargs.pop('user', None)
        super(AlunoForm, self).__init__(*args, **kwargs)
        self.fields['curso'].queryset = self.escola.cursos.all()
        self.fields['natural_municipio'].initial = self.escola.municipio
        self.fields['nacionalidade'].initial = self.escola.pais.get_nacionalidade()


    class Meta:
        model = Aluno
        widgets = {'natural_municipio': SelectMunicipioWidget}
        exclude = ('user',
                   'escola',
                   'date_add',
                   'date_upd',
                   'user_add',
                   'user_upd',
                   'responsaveis')

    def clean_rg(self):
        rg = self.cleaned_data['rg']
        if rg:
            return set_only_number(rg)
        return


    def save(self, *args, **kwargs):
        if not self.instance.pk:
            self.instance.user_add = self.user
        self.instance.user_upd = self.user
        self.instance.escola = self.escola
        instance = super(AlunoForm, self).save(*args, **kwargs)
        instance.save()

        return instance

class EmailRespensavelForm(forms.ModelForm):
    email = forms.EmailField(label='Email', required=True)

    def __init__(self, *args, **kwargs):
        super(EmailRespensavelForm, self).__init__(*args, **kwargs)

        self.fields['email'].label = 'Email do(a) resp. financeiro: %s ' % self.instance.nome
        

    class Meta:
        model = MembroFamilia
        fields = ['email',]


class EmailPessoaForm(forms.ModelForm):
    email = forms.EmailField(label='Email', required=True)
    # titulo = forms.CharField(label='Título da mensagem', initial='Parabéns pelo seu aniversário', required=True)
    mensagem = forms.CharField(widget=forms.Textarea, required=True)
    # assinatura = forms.CharField(label='Assinatura da mensagem', required=True)

    def __init__(self, *args, **kwargs):
        self.pessoa = kwargs.pop('pessoa', None)
        self.escola = kwargs.pop('escola', None)
        super(EmailPessoaForm, self).__init__(*args, **kwargs)

        self.fields['email'].label = 'Email do(a) aniversariante:'
        
        msg_default = MensagemDefault.objects.get(tipo=2, escola=self.escola)

        modelo = "{titulo}".format(titulo=msg_default.titulo)
        modelo += "\n{cabecalho}".format(cabecalho=msg_default.cabecalho)
        modelo += "\n\n{corpo}".format(corpo=msg_default.corpo)
        modelo = modelo.format(
            data=date.today().strftime("%d/%m/%Y"),
            nome_completo=self.instance.nome
        )
        modelo += "\n\n{assinatura}".format(assinatura=msg_default.assinatura)
        self.fields['mensagem'].initial = modelo

    class Meta:
        model = Pessoa
        fields = ['email',]


class MembroFamiliaForm(forms.ModelForm):
    cpf = BRCPFField(required=True, always_return_formated=True, return_format=u'%s%s%s%s',help_text='Somente números')
    sexo = forms.ChoiceField(label= 'Sexo',choices=SEXO_CHOICES)
    nascimento = forms.DateField(label='Data Nascimento', required=False, widget=DateTimePicker(options={"format": "DD/MM/YYYY", "pickTime": False}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.aluno = kwargs.pop('aluno', None)
        super(MembroFamiliaForm, self).__init__(*args, **kwargs)
        # import pdb; pdb.set_trace()

    def clean_rg(self):
        rg = self.cleaned_data['rg']
        if rg:
            return set_only_number(rg)
        return

    def save(self, *args, **kwargs):
        # ## SE o membro já existe no BD, não vai criar, vai só adicionar 'no' Aluno
        # ## pois pode estar cadastrado em outro Aluno ('irmão')
        cpf = set_only_number(self.instance.cpf)
        membro = None
        if not self.instance.id:
            membro = MembroFamilia.objects.filter(cpf=cpf).first()
            if membro:
                # Não cria um 'novo' o vínculo será criado
                # para o membro da família existente
                self.instance = membro
        self.instance.escola = self.aluno.escola
        if not self.instance.pk:
            self.instance.user_add = self.user
        self.instance.user_upd = self.user
        instance = super(MembroFamiliaForm, self).save(*args, **kwargs)

        instance.save()
        return instance

    class Meta:
        model = MembroFamilia
        fields = ['celular',
                  'cpf',
                  'documento',
                  'email',
                  'empresa',
                  'nascimento',
                  'nome',
                  'obs_empresa',
                  'profissao',
                  'rg',
                  'sexo',
                  'telefone',
                  'telefone_empresa']

class ResponsavelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.aluno = kwargs.pop('aluno', None)
        self.membro = kwargs.pop('membro', None)
        super(ResponsavelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Responsavel
        fields = ['parentesco',
                  'responsavel_financeiro',
                  'responsavel_pedagogico']

    def save(self, *args, **kwargs):
        self.instance.aluno = self.aluno
        instance = super(ResponsavelForm, self).save(*args, **kwargs)
        instance.save()
        return instance


class PessoaSearchForm(forms.Form):
    '''
    #33
    '''
    # responsavel = forms.CharField(label=u'Responsável', required=False)
    nome = forms.CharField(label=u'Nome: ', required=False)
    month = forms.ChoiceField(label='mês: ', choices=CHOICE_MONTH, initial=INITIAL_MONTH, required=False)
    ano = forms.ChoiceField(label='ano do contrato: ', choices=ANO, required=False)
    day = forms.IntegerField(label='dia: ', initial=date.today().day, required=False)
    # serie = forms.ModelChoiceField(label=u'Série', queryset=Serie.objects.all(), required=False)
    # curso = forms.ModelChoiceField(label=u'Curso', queryset=Serie.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        self.escola = kwargs.pop('escola', None)
        super(PessoaSearchForm, self).__init__(*args, **kwargs)

        self.contratos = apps.get_model('financeiro', 'ContratoAluno')


    def get_result_queryset(self, ano=None):
        pessoas = Pessoa.objects.filter(
            escola=self.escola).annotate(
            month=Extract('nascimento', 'month'),
            day=Extract('nascimento', 'day')
        )
        q = Q(escola=self.escola)
        # TODAS as PESSOA s que tem algum CONTRATO com a ESCOLA
        alunos_ativos_ids = self.contratos.objects.filter(
            aluno__escola=self.escola).values_list('aluno__id', flat=True)
        resp_ativos_ids = self.contratos.objects.filter(
            aluno__escola=self.escola).values_list('responsavel__id', flat=True)
        q = q & Q(id__in=alunos_ativos_ids) | Q(id__in=resp_ativos_ids)
        
        if self.is_valid():

            ano = self.cleaned_data['ano']
            if ano:
                ano = int(ano)
                # COM ANO só 'pega' as PESSOAs  que tem contrato naquele ano
                alunos_ativos_ids = self.contratos.objects.filter(ano=ano).values_list('aluno__id', flat=True)
                resp_ativos_ids = self.contratos.objects.filter(ano=ano).values_list('responsavel__id', flat=True)
                q = q & Q(id__in=alunos_ativos_ids) | Q(id__in=resp_ativos_ids)

            nome = self.cleaned_data['nome']
            if nome:
                q = q & Q(nome__icontains=nome)
            month = self.cleaned_data['month']
            if month:
                q = q & Q(month=int(month))
            day = self.cleaned_data['day']
            if day:
                q = q & Q(day=int(day))
            # serie = self.cleaned_data['serie']
            # if serie and ano:
            #     q = q & Q(contrato_aluno__ano=int(ano), contrato_aluno__serie=serie)

            # curso = self.cleaned_data['curso']
            # if curso and ano:
            #     q = q & Q(contrato_aluno__ano=int(ano), curso=curso)

            return pessoas.filter(q).order_by('month', 'day')
        return pessoas.filter(q).order_by('month', 'day')


class AlunoSearchForm(forms.Form):
    '''
    #33
    '''
    # responsavel = forms.CharField(label=u'Responsável', required=False)
    nome = forms.CharField(label=u'Nome', required=False)
    ano = forms.ChoiceField(label='Ano', choices=ANO, initial=ano_corrente, required=False)
    serie = forms.ModelChoiceField(label=u'Série', queryset=Serie.objects.all(), required=False)
    curso = forms.ModelChoiceField(label=u'Curso', queryset=Curso.objects.all(), required=False)
    situacao =  forms.ChoiceField(
        choices=COM_SEM_CONTRATO,
        widget=forms.RadioSelect(), required=False
    )

    def __init__(self, *args, **kargs):
        self.escola = kargs.pop('escola', None)
        super(AlunoSearchForm, self).__init__(*args, **kargs)
        cursos_ids = self.escola.cursos.all().values_list('id', flat=True)
        self.fields['serie'].queryset = Serie.objects.filter(curso__id__in=cursos_ids)
        self.fields['curso'].queryset = self.escola.cursos.all()
        self.contratos = apps.get_model('financeiro', 'ContratoAluno')

    def get_result_queryset(self):
        q = Q(escola=self.escola)

        exclude_ids = []

        if self.is_valid():
            ano = self.cleaned_data['ano']
            if ano:
                ano = int(ano)
                q = q & Q(ano=ano)
                alunos_com_contrato_ids = list(
                    self.contratos.objects.filter(ano=ano).values_list('aluno__id', flat=True)
                )
                q = q | Q(id__in=alunos_com_contrato_ids)

            nome = self.cleaned_data['nome']
            if nome:
                q = q & Q(nome__icontains=nome)

            serie = self.cleaned_data['serie']
            if serie and ano:
                q = q & Q(contrato_aluno__ano=ano, contrato_aluno__serie=serie)

            curso = self.cleaned_data['curso']
            if curso and ano:
                q = q & Q(contrato_aluno__ano=ano, curso=curso)

            situacao = self.cleaned_data['situacao']
            if situacao and ano:
                if situacao == '1':
                    q = q & Q(id__in=alunos_com_contrato_ids)
                elif situacao == '2':
                    exclude_ids = alunos_com_contrato_ids


            return Aluno.objects.filter(q).exclude(id__in=exclude_ids)
        return Aluno.objects.filter(q)


class ProfessorForm(forms.ModelForm):
    ativo = forms.BooleanField(label='Ativo', required=False)

    class Meta:
        model = UserGrupos
        # exclude = ('user', 'date_joined', 'escola', 'grupo')
        fields = ('ativo',)


class ClasseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.escola = kwargs.pop('escola', None)
        super(ClasseForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.escola = self.escola
        instance = super(ClasseForm, self).save(*args, **kwargs)
        instance.save()
        return instance

    class Meta:
        model = Classe
        exclude = ('escola',)


class ClasseAlunoForm(forms.ModelForm):
    aluno = forms.ModelChoiceField(label="Selecione o aluno:", queryset=User.objects.all())

    class Meta:
        model = ClasseAluno
        fields = ('aluno',)

    def __init__(self, *args, **kwargs):
        self.classe = kwargs.pop('classe', None)
        super(ClasseAlunoForm, self).__init__(*args, **kwargs)

        escola = Escola.objects.get(id=self.classe.escola.id)
        alunos_ids = UserGrupos.objects.filter(escola=escola, grupo__name='Aluno').values_list('user__id', flat=True)
        classes_concorrentes_ids = Classe.objects.filter(ano=self.classe.ano, escola=escola).values_list('id', flat=True)
        alunos_distribuidos_ids = ClasseAluno.objects.filter(classe__id__in=classes_concorrentes_ids).values_list('aluno__id', flat=True)
        alunos_disponiveis_ids = list(set(alunos_ids)-set(alunos_distribuidos_ids))

        self.fields['aluno'].queryset = User.objects.filter(id__in=alunos_disponiveis_ids)

    def save(self, *args, **kwargs):
        self.instance.classe = self.classe
        instance = super(ClasseAlunoForm, self).save(*args, **kwargs)
        instance.save()
        return instance

class ClasseProfessorForm(forms.ModelForm):
    professor = forms.ModelChoiceField(label="Selecione o professor:", queryset=User.objects.all())

    class Meta:
        model = ClasseProfessor
        fields = ('professor', 'materia')

    def __init__(self, *args, **kwargs):
        self.classe = kwargs.pop('classe', None)
        super(ClasseProfessorForm, self).__init__(*args, **kwargs)

        escola = Escola.objects.get(id=self.classe.escola.id)
        professors_ids = UserGrupos.objects.filter(escola=escola, grupo__name='Professor').values_list('user__id', flat=True)
       
        # classes_concorrentes_ids = Classe.objects.filter(ano=self.classe.ano, escola=escola).values_list('id', flat=True)
        # professors_distribuidos_ids = ClasseProfessor.objects.filter(classe__id__in=classes_concorrentes_ids).values_list('professor__id', flat=True)
        # professors_disponiveis_ids = list(set(professors_ids)-set(professors_distribuidos_ids))

        self.fields['professor'].queryset = User.objects.filter(id__in=professors_ids)

    def save(self, *args, **kwargs):
        self.instance.classe = self.classe
        instance = super(ClasseProfessorForm, self).save(*args, **kwargs)
        instance.save()
        return instance