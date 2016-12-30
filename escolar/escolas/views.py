
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from escolar.core.models import UserGrupos, User
from django.contrib.auth.models import Group

from escolar.escolas.models import (
    Escola,
)
from escolar.escolas.forms import (
    AlunoForm,
    EscolaForm,
    GrupoForm,
    )

@login_required
def escolas_list(request):
    user = request.user
    escolas_ids = user.usergrupos_set.filter(grupo__name='Diretor').values_list('escola__id', flat=True)
    if user.is_admin():
        escolas = Escola.objects.all()
    else:
        escolas =  Escola.objects.filter(id__in=escolas_ids)
    return render(request, 'escolas/escolas_list.html', {'escolas': escolas})


@login_required
def escola_form(request, pk=None):
    if pk:
        escola = get_object_or_404(Escola, pk=pk)
        msg = u'Escola alterada com sucesso.'
    else:
        escola = None
        msg = u'Escola criada.'

    form = EscolaForm(request.POST or None, instance=escola)

    if request.method == 'POST':
        if form.is_valid():
            escola = form.save()
            messages.success(request, msg)
            return redirect(reverse('escolas_list'))
        else:
            messages.warning(request, u'Falha no cadastro de escola')

    return render(request,
                        'escolas/escola_form.html', {
                        'form': form})


@login_required
def grupos_list(request):

    grupos = Group.objects.all()
    context = {}
    context['grupos'] = grupos
    return render(request, 'escolas/grupos_list.html', context)


@login_required
def grupo_form(request, grupo_pk=None):
    if grupo_pk:
        grupo = get_object_or_404(Grupo, pk=grupo_pk)
        msg = u'Grupo alterado com sucesso.'
    else:
        grupo = None
        msg = u'Grupo criado.'

    form = GrupoForm(request.POST or None, instance=grupo)

    if request.method == 'POST':
        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.save()
            messages.success(request, msg)
            return redirect(reverse('grupos_list'))
        else:
            messages.warning(request, u'Falha no cadastro do grupo')

    context = {}
    context['form'] = form

    return render(request, 'escolas/grupo_form.html', context)


@login_required
def professores_list(request):
    user = request.user
    escolas_ids = user.usergrupos_set.filter(grupo__name='Diretor').values_list('escola__id', flat=True)
    professores_ids = UserGrupos.objects.filter(grupo__name='Professor',escola__pk__in=escolas_ids).values_list('user__id', flat=True)
    context = {}
    context['professores'] = User.objects.filter(id__in=professores_ids)

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

    return render(request, 'escolas/grupo_form.html', context)


@login_required
def alunos_list(request):
    user = request.user
    escolas_ids = user.usergrupos_set.filter(grupo__name='Diretor').values_list('escola__id', flat=True)
    alunos_ids = UserGrupos.objects.filter(grupo__name='Aluno',escola__pk__in=escolas_ids).values_list('user__id', flat=True)
    context = {}
    context['alunos'] = User.objects.filter(id__in=alunos_ids)

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

    return render(request, 'escolas/aluno_form.html', context)
