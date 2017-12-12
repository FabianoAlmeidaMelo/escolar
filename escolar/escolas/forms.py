# coding: utf-8
from django import forms

#from localflavor.br.forms import BRCPFField  # 1.4
# from localbr.formfields import BRCPFField
from escolar.escolas.models import (
    Autorizado,
    AutorizadoAluno,
    Escola,
    Classe,
    ClasseAluno,
    ClasseProfessor,
    )
from escolar.core.models import User, UserGrupos


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
    ativo = forms.BooleanField(label='Matriculado', required=False)

    class Meta:
        model = UserGrupos
        # exclude = ('date_joined', 'escola', 'grupo')
        fields = ('ativo',)

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