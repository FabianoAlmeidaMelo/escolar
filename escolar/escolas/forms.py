# coding: utf-8
from datetime import date
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.db.models import Q
from django import forms
from municipios.widgets import SelectMunicipioWidget

from localbr.formfields import BRCPFField, BRCNPJField, BRPhoneNumberField


from escolar.escolas.models import (
    Aluno,
    ANO,
    Autorizado,
    AutorizadoAluno,
    Escola,
    Classe,
    ClasseAluno,
    ClasseProfessor,
    MembroFamilia,
)

from escolar.core.models import User, UserGrupos

hoje = date.today()
ano_corrente = hoje.year

SEXO_CHOICES = (
    (None, '---'),
    (1, 'Masculino'),
    (2, 'Feminino'),
)

def set_only_number(txt):
    especiais = '_-./;^;ç=*&%$#@!'
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
        autorizado, create = Autorizado.objects.get_or_create(documento=self.instance.documento,
                                                              defaults={'email': self.instance.email,
                                                                        'nome': self.instance.nome, 
                                                                        'celular': self.instance.celular})
        
        autorizado_aluno, created = AutorizadoAluno.objects.get_or_create(escola=self.escola,
                                                                          aluno=self.aluno,
                                                                          autorizado=autorizado,
                                                                          defaults={'responsavel': self.responsavel,
                                                                                    'status': True})
        instance = autorizado
        instance.save()
        return instance


    class Meta:
        model = Autorizado
        fields = ('nome', 'email', 'celular', 'documento') 

class EscolaForm(forms.ModelForm):
    logo = forms.ImageField(label='Logo', required=False)
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EscolaForm, self).__init__(*args, **kwargs)
        if not self.user.is_admin():
            self.fields['publica'].widget = forms.HiddenInput()

    class Meta:
        model = Escola
        exclude = ('created_at',)


class AlunoForm(forms.ModelForm):
    ra = forms.CharField(label='RA', required=False)
    cpf = BRCPFField(required=False, always_return_formated=True, return_format=u'%s%s%s%s', help_text='Somente números')

    def __init__(self, *args, **kwargs):
        self.escola = kwargs.pop('escola', None)
        self.user = kwargs.pop('user', None)
        super(AlunoForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Aluno
        widgets = {'natural_municipio': SelectMunicipioWidget}
        exclude = ('user', 'escola', 'date_add', 'date_upd', 'user_add', 'user_upd')

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


class MembroFamiliaForm(forms.ModelForm):
    cpf = BRCPFField(required=False, always_return_formated=True, return_format=u'%s%s%s%s',help_text='Somente números')
    sexo = forms.ChoiceField(label= 'Sexo',choices=SEXO_CHOICES)
    # celular = BRPhoneNumberField(label='Celular', required=False)
    # telefone = BRPhoneNumberField(label='Telefone', required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.aluno = kwargs.pop('aluno', None)
        super(MembroFamiliaForm, self).__init__(*args, **kwargs)

    def clean_rg(self):
        rg = self.cleaned_data['rg']
        if rg:
            return set_only_number(rg)
        return

    def save(self, *args, **kwargs):
        if not self.instance.pk:
            self.instance.user_add = self.user
        self.instance.user_upd = self.user
        self.instance.aluno = self.aluno

        instance = super(MembroFamiliaForm, self).save(*args, **kwargs)
        instance.save()
        return instance

    class Meta:
        model = MembroFamilia
        fields = ['parentesco',
                  'responsavel_financeiro',
                  'responsavel_pedagogico',
                  'nome',
                  'nascimento',
                  'profissao',
                  'sexo',
                  'cpf',
                  'rg',
                  'email',
                  'celular',
                  'empresa',
                  'obs_empresa',
                  'documento',
                  'telefone_empresa',
                  'telefone']


class AlunoSearchForm(forms.Form):
    '''
    #33
    '''
    # responsavel = forms.CharField(label=u'Responsável', required=False)
    nome = forms.CharField(label=u'Nome', required=False)
    ano = forms.ChoiceField(label='Ano', choices=ANO, initial=ano_corrente)
    serie = forms.CharField(label=u'Série', required=False)
    curso = forms.CharField(label=u'Curso', required=False)

    def __init__(self, *args, **kargs):
        self.escola = kargs.pop('escola', None)
        super(AlunoSearchForm, self).__init__(*args, **kargs)
       

    def get_result_queryset(self):
        q = Q(escola=self.escola)
        if self.is_valid():
            # responsavel = self.cleaned_data['responsavel']
            # if responsavel:
            #     q = q & Q(responsavel__nome__icontains=responsavel)
            nome = self.cleaned_data['nome']
            if nome:
                q = q & Q(nome__icontains=nome)
            ano = self.cleaned_data['ano']
            if ano:
                q = q & Q(contrato_aluno__ano=int(ano))

            serie = self.cleaned_data['serie']
            if serie and ano:
                q = q & Q(contrato_aluno__ano=int(ano), contrato_aluno__serie__icontains=serie)

            curso = self.cleaned_data['curso']
            if curso and ano:
                q = q & Q(contrato_aluno__ano=int(ano), contrato_aluno__curso__icontains=curso)

        return Aluno.objects.filter(q)


# class AlunoForm(forms.ModelForm):
#     ativo = forms.BooleanField(label='Matriculado', required=False)

#     class Meta:
#         model = UserGrupos
#         # exclude = ('date_joined', 'escola', 'grupo')
#         fields = ('ativo',)

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