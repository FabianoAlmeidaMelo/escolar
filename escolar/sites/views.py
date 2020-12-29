# coding: utf-8
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
    resolve_url,
)

from escolar.escolas.models import(
    Escola,
)

from escolar.sites.models import(
    Conteudo,
)
from escolar.sites.forms import (
    ConteudoForm,
)

@login_required
def conteudo_form(request, escola_pk, conteudo_pk=None):
    user = request.user

    escola = get_object_or_404(Escola, pk=escola_pk)
    if not user.is_diretor(escola.pk):
        raise Http404
    if conteudo_pk:
        contrato = get_object_or_404(Conteudo, pk=conteudo_pk)
        msg = u'Conteúdo alterado com sucesso.'
    else:
        conteudo = None
        msg = u'Conteúdo criado.' 
    can_edit = all([user.is_diretor(escola.id)])
    if not can_edit:
        raise Http404

    form = ConteudoForm(
    	request.POST or None,
    	request.FILES or None,
    	instance=conteudo,
    	escola=escola,
    	user=user
    )
    context = {}
    context['form'] = form
    context['conteudo'] = conteudo
    context['escola'] = escola
    context['can_edit'] = can_edit
    context['tab_alunos'] = "active"
    context['tab_aluno_contratos'] = "active"

    if request.method == 'POST':
        if form.is_valid():
            conteudo = form.save()
            messages.success(request, msg)
            # return redirect(reverse('contrato_cadastro', kwargs={'conteudo_pk': conteudo.pk}))
        else:
            messages.warning(request, u'Falha no cadastro do conteúdo.')

    return render(request, 'sites/conteudo_form.html', context)