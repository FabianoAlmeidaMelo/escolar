# coding: utf-8
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, resolve_url

from escolar.core.models import User, UserGrupos
from escolar.core.forms import UserForm

def home(request):
    return render(request, 'index.html') #, context)

@login_required
def usuarios_list(request):
    '''
    listagem vazia, mostrando somente o que aparece no filtro? OU
    lista todos os usuários da escola?
    '''
    context = {}
    usuarios = User.objects.all()
    context['usuarios'] = usuarios

    return render(request, 'core/usuarios_list.html', context)


@login_required
def usuario_form(request, pk=None):
    '''
    '''
    if pk:
        usuario = get_object_or_404(User, pk=pk)
        msg = u'Usuário alterado com sucesso.'
    else:
        usuario = None
        msg = u'Usuário cadastrado.'

    form = UserForm(request.POST or None, instance=usuario)

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
