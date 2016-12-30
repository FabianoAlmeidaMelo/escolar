# coding: utf-8
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, resolve_url

from escolar.core.models import User, UserGrupos
from escolar.core.forms import UserForm

def home(request):
    return render(request, 'index.html')

@login_required
def usuarios_list(request):
    '''
    Admin: todos
    Diretor: users da escola dele
    Outros: os próprios
    '''
    user = request.user
    escolas_ids = user.usergrupos_set.filter(grupo__name='Diretor').values_list('escola__id', flat=True)
    if user.is_admin():
        usuarios = User.objects.all()
    elif escolas_ids:
        usuarios_ids = UserGrupos.objects.filter(escola__pk__in=escolas_ids).values_list('user__id', flat=True)
        usuarios = User.objects.filter(id__in=usuarios_ids)
    else:
        usuarios = User.objects.filter(id=user.id)
    context = {}
    context['usuarios'] = usuarios

    return render(request, 'core/usuarios_list.html', context)


@login_required
def usuario_form(request, pk=None):
    '''
    Admin: cria, seta senha, vincula a Escola e Group
    Diretor: cria e ou vincula a Escola (dele) e Grupo
    Outros: edita email, nome e troca senha
    '''
    user = request.user
    if pk:
        usuario = get_object_or_404(User, pk=pk)
        msg = u'Usuário alterado com sucesso.'
    else:
        usuario = None
        msg = u'Usuário cadastrado.'

    form = UserForm(request.POST or None, instance=usuario, user=user)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            msg += user.nome
            messages.success(request, msg)
        else:
            messages.warning(request, u'Falha no cadastro do Aluno')
        return redirect(reverse('usuarios_list'))

    context = {}
    context['form'] = form

    return render(request, 'core/usuario_form.html', context)
