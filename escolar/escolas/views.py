
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from escolar.core.models import UserGrupos, User
from django.contrib.auth.models import Group

from escolar.escolas.models import (
    Escola,
)
from escolar.escolas.forms import (
    AlunoForm,
    EscolaForm,
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
def professor_form(request, escola_pk, grupo_user_pk=None):
    escola = Escola.objects.get(id=escola_pk)
    grupo = Group.objects.filter(nome='Professor')

    if grupo_user_pk:
        grupo_user = get_object_or_404(GrupoUser, pk=grupo_user_pk)
        msg = u'Professor alterado com sucesso.'
    else:
        grupo_user = None
        msg = u'Professor criado.'

    form = GrupoUserForm(request.POST or None, instance=grupo_user, escola=escola)

    if request.method == 'POST':
        if form.is_valid():
            grupo_user = form.save(commit=False)
            grupo_user.escola = escola
            grupo_user.save()
            messages.success(request, msg)
            return redirect(reverse('professores_list'))
        else:
            messages.warning(request, u'Falha no cadastro do Professor')

    context = {}
    context['form'] = form
    context['escola'] = escola
    context['grupo_user'] = grupo_user
    context['tab_professores'] = "active"

    return render(request, 'escolas/grupo_form.html', context)


@login_required
def alunos_list(request, escola_pk):
    user = request.user
    alunos_ids = UserGrupos.objects.filter(grupo__name='Aluno',escola__pk=escola_pk).values_list('user__id', flat=True)
    context = {}
    context['alunos'] = User.objects.filter(id__in=alunos_ids)
    context['escola'] = Escola.objects.get(id=escola_pk)
    context['can_edit'] = any([user.is_admin(), user.is_diretor(escola_pk)])
    context['user'] = user
    context['tab_alunos'] = "active"

    return render(request, 'escolas/alunos_list.html', context)


@login_required
def aluno_form(request, escola_pk, aluno_pk=None):
    '''
    aluno é user
    '''
    escola = Escola.objects.get(id=escola_pk)
    grupo = Group.objects.filter(nome='Aluno')

    if aluno_pk:
        aluno = get_object_or_404(GrupoUser, pk=aluno_pk)
        msg = u'Aluno alterado com sucesso.'
    else:
        aluno = None
        msg = u'Aluno cadastrado.'

    form = AlunoForm(request.POST or None, instance=aluno, escola=escola)

    if request.method == 'POST':
        if form.is_valid():
            # grupo_user = form.save(commit=False)
            # grupo_user.escola = escola
            # grupo_user.save()
            messages.success(request, msg)
            return redirect(reverse('alunos_list'))
        else:
            messages.warning(request, u'Falha no cadastro do Aluno')

    context = {}
    context['form'] = form
    context['escola'] = escola
    context['grupo_user'] = grupo_user
    context['tab_alunos'] = "active"

    return render(request, 'escolas/aluno_form.html', context)
