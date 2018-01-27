# coding: utf-8
from datetime import date
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.db.models import Q
from django import forms
from municipios.widgets import SelectMunicipioWidget
#from localflavor.br.forms import BRCPFField  # 1.4
# from localbr.formfields import BRCPFField
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

class AutorizadoForm(forms.ModelForm):
    '''#22'''
    documento = forms.CharField(label='Documento')

    def __init__(self, *args, **kwargs):
        self.escola = kwargs.pop('escola', None)
        self.aluno = kwargs.pop('aluno', None)
        self.responsavel = kwargs.pop('responsavel', None)
        super(AutorizadoForm, self).__init__(*args, **kwargs)

        # TODO: verificar o localflavor
        # if self.escola.pais.sigla == 'BRA':
        #     self.fields['documento'] = BRCPFField(required=True,
        #                                           always_return_formated=True,
        #                                           return_format=u'%s%s%s%s',
        #                                           help_text='ex: 000.000.000-00')
        self.fields['documento'].label = 'CPF'

    def save(self, *args, **kwargs):
        autorizado, create = Autorizado.objects.get_or_create(email=self.instance.email,
                                                              defaults={'nome': self.instance.nome, 
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
    # natural_municipio = forms.IntegerField(label=u"Natural de: UF - Município", widget=SelectMunicipioWidget)

    def __init__(self, *args, **kwargs):
        self.escola = kwargs.pop('escola', None)
        self.user = kwargs.pop('user', None)
        super(AlunoForm, self).__init__(*args, **kwargs)
        # self.fields['natural_municipio'].widgets = SelectMunicipioWidget
        # self.fields['natural_municipio'].label = 'Natural de'

    class Meta:
        model = Aluno
        widgets = {'natural_municipio': SelectMunicipioWidget}
        exclude = ('user', 'escola', 'date_add', 'date_upd', 'user_add', 'user_upd')


    def save(self, *args, **kwargs):
        if not self.instance.pk:
            self.instance.user_add = self.user
        self.instance.user_upd = self.user
        self.instance.escola = self.escola
        instance = super(AlunoForm, self).save(*args, **kwargs)
        instance.save()
        return instance


class MembroFamiliaForm(forms.ModelForm):
    sexo = forms.ChoiceField(label= 'Sexo',choices=SEXO_CHOICES)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(MembroFamiliaForm, self).__init__(*args, **kwargs)

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
                  'documento']



class BaseMembroFamiliaFormSet(BaseInlineFormSet):

    def get_queryset(self):
        '''
        Customizado para ordenar por Parcela
        1, 2, ...
        origem:
        http://stackoverflow.com/questions/13387446/changing-the-display-order-of-forms-in-a-formset
        '''
        if not hasattr(self, '_queryset'):
            if self.queryset is not None:
                qs = self.queryset
            else:
                qs = self.model._default_manager.get_query_set()

            qs = qs.order_by('id')
            # /MOD

            # Removed queryset limiting here. As per discussion re: #13023
            # on django-dev, max_num should not prevent existing
            # related objects/inlines from being displayed.
            self._queryset = qs
        return self._queryset


MembroFamiliaFormSet = inlineformset_factory(
    parent_model=Aluno,
    model=MembroFamilia,
    form=MembroFamiliaForm,
    formset=BaseMembroFamiliaFormSet,
    fields=('parentesco',
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
            ),
    # can_order=True,
    can_delete=True,
    extra=1
    )



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
                q = q & Q(ano=ano)

            serie = self.cleaned_data['serie']
            if serie:
                q = q & Q(serie__icontains=serie)
            curso = self.cleaned_data['curso']
            if curso:
                q = q & Q(curso__icontains=curso)

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