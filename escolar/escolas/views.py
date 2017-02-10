
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from escolar.core.models import UserGrupos, User
from django.contrib.auth.models import Group

from escolar.escolas.models import (
    Escola,
    Classe,
    ClasseAluno,
)
from escolar.escolas.forms import (
    AlunoForm,
    ClasseForm,
    ClasseAlunoForm,
    EscolaForm,
    ProfessorForm,
    )

@login_required
def escolas_list(request):
    user = request.user
    escolas_ids = user.usergrupos_set.all().values_list('escola__id', flat=True)
    if user.is_admin():
        escolas = Escola.objects.all()
    else:
        escolas =  Escola.objects.filter(id__in=escolas_ids)
    context = {}
    context['can_create'] = user.is_admin()
    context['escolas'] = escolas
    context['tab_escola'] = "active"
    return render(request, 'escolas/escolas_list.html', context)


@login_required
def escola_form(request, pk=None):
    user = request.user
    admin = can_edit = user.is_admin()
    if pk:
        escola = get_object_or_404(Escola, pk=pk)
        msg = u'Escola alterada com sucesso.'
        can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
        if not can_edit:
            raise Http404
    else:
        escola = None
        msg = u'Escola criada.' 

    form = EscolaForm(request.POST or None, instance=escola)
    context = {}
    context['form'] = form
    context['escola'] = escola
    context['admin'] = admin
    context['tab_escola'] = "active"

    if request.method == 'POST':
        if form.is_valid():
            escola = form.save()
            messages.success(request, msg)
            return redirect(reverse('escolas_list'))
        else:
            messages.warning(request, u'Falha no cadastro de escola')

    return render(request, 'escolas/escola_form.html', context)


@login_required
def escola_cadastro(request, pk):
    user = request.user
    escola =  Escola.objects.get(id=pk)
    can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
    context = {}
    context["escola"] = escola
    context['tab_escola'] = "active"
    context['can_edit'] = can_edit
    return render(request, 'escolas/escola_cadastro.html', context)


@login_required
def professores_list(request, escola_pk):
    user = request.user
    escola = Escola.objects.get(id=escola_pk)
    professores_ids = UserGrupos.objects.filter(grupo__name='Professor',escola__pk=escola_pk).values_list('user__id', flat=True)
    context = {}
    context['escola'] = escola
    context['professores'] = User.objects.filter(id__in=professores_ids)
    context['can_edit'] = any([user.is_admin(), user.is_diretor(escola_pk)])
    context['user'] = user
    context['tab_professores'] = "active"
    return render(request, 'escolas/professores_list.html', context)


@login_required
def professor_form(request, escola_pk, professor_pk=None):
    '''
    professor é user
    Não cria aqui, já foi definido no cadastro do user
    '''
    escola = Escola.objects.get(id=escola_pk)
    grupo = Group.objects.filter(name='Professor')
    professor = None
    if professor_pk:
        professor = User.objects.get(pk=professor_pk)

    if professor_pk:
        grupo_user = get_object_or_404(UserGrupos, escola=escola_pk, user=professor_pk, grupo=grupo)
        msg = u'Professor alterado com sucesso.'
    else:
        grupo_user = None
        msg = u'Professor cadastrado.'

    form = ProfessorForm(request.POST or None, instance=grupo_user)

    if request.method == 'POST':
        if form.is_valid():
            grupo_user = form.save()
            messages.success(request, msg)
            return redirect(reverse('professores_list', kwargs={'escola_pk': escola.pk}))
        else:
            messages.warning(request, u'Falha no cadastro do Professor')

    context = {}
    context['form'] = form
    context['escola'] = escola
    context['grupo_user'] = grupo_user
    context['tab_professores'] = "active"
    context['professor'] = professor

    return render(request, 'escolas/professor_form.html', context)


@login_required
def alunos_list(request, escola_pk):
    user = request.user
    alunos_ids = UserGrupos.objects.filter(grupo__name='Aluno',escola__pk=escola_pk).values_list('user__id', flat=True)
    context = {}
    escola = Escola.objects.get(id=escola_pk)
    alunos = User.objects.filter(id__in=alunos_ids)
    for aluno in alunos:
        aluno.classe = aluno.get_classe(escola)
        aluno.status = aluno.usergrupos_set.filter(grupo__name='Aluno', escola=1).last().ativo
    context['alunos'] = alunos
    context['escola'] = escola 
    context['can_edit'] = any([user.is_admin(), user.is_diretor(escola_pk)])
    context['user'] = user
    context['tab_alunos'] = "active"

    return render(request, 'escolas/alunos_list.html', context)


@login_required
def aluno_form(request, escola_pk, aluno_pk=None):
    '''
    aluno é user
    Não cria aqui, já foi definido no cadastro do user
    '''
    escola = Escola.objects.get(id=escola_pk)
    grupo = Group.objects.filter(name='Aluno')
    aluno = None
    if aluno_pk:
        aluno = User.objects.get(pk=aluno_pk)

    if aluno_pk:
        grupo_user = get_object_or_404(UserGrupos, escola=escola_pk, user=aluno_pk, grupo=grupo)
        msg = u'Aluno alterado com sucesso.'
    else:
        grupo_user = None
        msg = u'Aluno cadastrado.'

    form = AlunoForm(request.POST or None, instance=grupo_user)

    if request.method == 'POST':
        if form.is_valid():
            grupo_user = form.save()
            messages.success(request, msg)
            return redirect(reverse('alunos_list', kwargs={'escola_pk': escola.pk}))
        else:
            messages.warning(request, u'Falha no cadastro do Aluno')

    context = {}
    context['form'] = form
    context['escola'] = escola
    context['grupo_user'] = grupo_user
    context['tab_alunos'] = "active"
    context['aluno'] = aluno
    context['classes'] = aluno.get_all_classe(escola)

    return render(request, 'escolas/aluno_form.html', context)


@login_required
def classe_form(request, escola_pk, classe_pk=None):
    '''
    Classes "isolarão":
    escola;
    curso, ex: 5º ano ensino fundamental A, 5º ano B, ...
    ano: 2017, 2018, ...
    período: manhã, tarde, noite
    >>
    professores que dão aula para determinada classe
    alunos que pertencem a uma classe

    user não pode trocar o ID da escola
    '''
    escola = Escola.objects.get(id=escola_pk)

    classe = None
    msg = u'Classe cadastrada.'

    if classe_pk:
        classe = get_object_or_404(Classe, pk=classe_pk)
        msg = u'Classe alterada com sucesso.'

    form = ClasseForm(request.POST or None, instance=classe, escola=escola)

    if request.method == 'POST':
        if form.is_valid():
            classe = form.save()
            messages.success(request, msg)
            return redirect(reverse('classes_list', kwargs={'escola_pk': escola.pk}))
        else:
            messages.warning(request, u'Falha no cadastro do Classe')

    context = {}
    context['form'] = form
    context['escola'] = escola
    context['classe'] = classe
    context['tab_classes'] = "active"

    return render(request, 'escolas/classe_form.html', context)


@login_required
def classes_list(request, escola_pk):
    user = request.user
    classes = Classe.objects.filter(escola__pk=escola_pk)
    context = {}
    context['classes'] = classes
    context['escola'] = Escola.objects.get(id=escola_pk)
    context['can_edit'] = any([user.is_admin(), user.is_diretor(escola_pk)])
    context['user'] = user
    context['tab_classes'] = "active"

    return render(request, 'escolas/classes_list.html', context)



@login_required
def classe_aluno_form(request, classe_pk, classe_aluno_pk=None):
    classe = get_object_or_404(Classe, pk=classe_pk)
    classe_aluno = None
    msg = 'Vinculação classe aluno criada'

    escola = Escola.objects.get(id=classe.escola.id)
    if classe_aluno_pk:
        classe_aluno = get_object_or_404(ClasseAluno, pk=classe_aluno_pk)
        msg = 'Vinculação classe aluno editada'

    form = ClasseAlunoForm(request.POST or None, instance=classe_aluno, classe=classe)

    if request.method == 'POST':
        if form.is_valid():
            classe_aluno = form.save()
            messages.success(request, msg)
            return redirect(reverse('classes_list', kwargs={'escola_pk': escola.pk}))
        else:
            messages.warning(request, u'Falha no cadastro do Aluno')

    context = {}
    context['form'] = form
    context['escola'] = escola
    context['classe_aluno'] = classe_aluno
    context['tab_classes'] = "active"
    context['classe'] = classe

    return render(request, 'escolas/classe_aluno_form.html', context)