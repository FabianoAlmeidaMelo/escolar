# coding: utf-8
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404, resolve_url

from escolar.core.models import User, UserGrupos
from escolar.core.forms import UserForm, GrupoForm

from escolar.escolas.models import Escola

def home(request):
    return render(request, 'index.html')


@login_required
def usuarios_list(request, escola_pk):
    '''
    Admin: todos
    Diretor: users da escola dele
    Outros: os próprios
    '''
    user = request.user
    page = request.GET.get('page', 1)
    context = {}
    diretor = user.is_diretor(escola_pk)
    admin = user.is_admin()
    if user.is_admin():
        usuarios = User.objects.all()
    elif diretor:
        usuarios_ids = UserGrupos.objects.filter(escola__pk=escola_pk).values_list('user__id', flat=True)
        usuarios = User.objects.filter(id__in=usuarios_ids)
    else:
        usuarios = User.objects.filter(id=user.id)

    paginator = Paginator(usuarios, 15)
    try:
        usuarios = paginator.page(page)
    except PageNotAnInteger:
        usuarios = paginator.page(1)
    except EmptyPage:
        usuarios = paginator.page(paginator.num_pages)

    context['object_list'] = usuarios #.order_by('nome')
    context['escola'] = Escola.objects.get(id=escola_pk)
    context['can_edit'] = diretor or admin
    context['tab_usuarios'] = "active"

    return render(request, 'core/usuarios_list.html', context)


@login_required
def usuario_form(request, escola_pk, pk=None):
    '''
    Admin: cria, seta senha, vincula a Escola e Group
    Diretor: cria e ou vincula a Escola (dele) e Grupo
    Outros: edita email, nome e troca senha
    '''
    escola = Escola.objects.get(pk=escola_pk)
    user = request.user
    if pk:
        usuario = get_object_or_404(User, pk=pk)
        msg = u'Usuário alterado com sucesso.'
    else:
        usuario = None
        msg = u'Usuário cadastrado.'

    form = UserForm(request.POST or None, instance=usuario, user=user)
    context = {}
    context['form'] = form
    context['escola'] = escola
    context['tab_usuarios'] = "active"

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            msg += user.nome
            messages.success(request, msg)
        else:
            messages.warning(request, u'Falha no cadastro do Aluno')
            return render(request, 'core/usuario_form.html', context)
        return redirect(reverse('usuarios_list', kwargs={'escola_pk': escola.pk}))


    return render(request, 'core/usuario_form.html', context)


@login_required
def grupos_list(request, escola_pk=None):
    escola = None
    if escola_pk:
        escola = Escola.objects.get(pk=escola_pk)
    user = request.user
    can_edit = user.is_admin()
    grupos = Group.objects.all()
    if escola:
        grupos = grupos.exclude(name='Admin')
    elif not escola and not can_edit:
        raise Http404
    context = {}
    context['grupos'] = grupos
    context['can_edit'] = can_edit
    context['escola'] = escola
    context['tab_grupos'] = "active"
    return render(request, 'core/grupos_list.html', context)


@login_required
def grupo_form(request, grupo_pk=None):
    user = request.user
    can_edit = user.is_admin()
    if not can_edit:
        raise Http404
    if grupo_pk:
        grupo = get_object_or_404(Group, pk=grupo_pk)
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

    return render(request, 'core/grupo_form.html', context)
