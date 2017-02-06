# coding: utf-8
from django import forms
from escolar.escolas.models import (
    Escola,
    Classe,
    ClasseAluno,
    )
from escolar.core.models import User, UserGrupos


class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        exclude = ('created_at', )


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
        # print("\n\nEscola", escola )
        # print("Todos alunos IDS:", alunos_ids)
        # print("CLASSES conc:", classes_concorrentes_ids)
        # print("A distr:", alunos_distribuidos_ids)
        # print("A dispon:", alunos_disponiveis_ids)
        self.fields['aluno'].queryset = User.objects.filter(id__in=alunos_disponiveis_ids)

    def save(self, *args, **kwargs):
        self.instance.classe = self.classe
        instance = super(ClasseAlunoForm, self).save(*args, **kwargs)
        instance.save()
        return instance