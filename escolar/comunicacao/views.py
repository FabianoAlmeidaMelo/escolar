# coding: utf-8
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.shortcuts import (
	render,
	redirect,
	get_object_or_404,
	resolve_url,
)
from escolar.comunicacao.models import(
    MensagemDefault
)
from escolar.comunicacao.forms import (
    MensagemDefaultForm,
)
from escolar.escolas.models import (
    Escola,
)
from escolar.financeiro.forms import (
    EmailMensagemForm,
)
from escolar.financeiro.models import (
    InadimplenteDBView,
)

@login_required
def msg_default_form(request, escola_pk, msg_pk):
    user = request.user
    escola = get_object_or_404(Escola, pk=escola_pk)

    escola = inadimplente.escola
    is_diretor = user.is_diretor(escola.pk)
    if not is_diretor:
        raise Http404

    if bandeira_pk:
        msg_default = get_object_or_404(MensagemDefault, pk=msg_pk)
        msg = u'Mensagem alterada com sucesso.'
    else:
        msg_default = None
        msg = u'Mensagem criada.'

    form = MensagemDefaultForm(request.POST or None, instance=inadimplente, user=user)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(reverse('inadimplentes_list', kwargs={'escola_pk': escola.pk}))
        else:
            messages.warning(request, u'Falha na edição da Mensagem.')

    context = {}
    context['form'] = form
    context['escola'] = escola
    context['msg_default'] = msg_default
    context['tab_sistema'] = "active"
    context['tab_mensagem_default'] = "active"
    context['can_edit'] = is_diretor

    return render(request, 'comunicacao/msg_default_form.html', context)


@login_required
def msg_default_list(request, escola_pk):
    '''
    Lista todas as Mensagens Default cadastradas para a escola
    '''
    escola = get_object_or_404(Escola, pk=escola_pk)
    user = request.user
    can_edit = user.is_diretor(escola.id)
    can_create = user.is_admin()
    msg_default_qs = MensagemDefault.objects.filter(escola=escola)

    context = {}
    context['msg_default_qs'] = msg_default_qs
    context['can_create'] = can_create
    context['can_edit'] = can_edit
    context['escola'] = escola
    context['tab_sistema'] = "active"
    context['tab_mensagem_default'] = "active"
    return render(request, 'comunicacao/msg_default_list.html', context)


@login_required
def cobranca_form(request, pk):
    user = request.user
    inadimplente = get_object_or_404(
        InadimplenteDBView,
        pk=pk
    )
    escola = inadimplente.escola
    is_diretor = user.is_diretor(escola.pk)
    if not is_diretor:
        raise Http404

    form = EmailMensagemForm(request.POST or None, instance=inadimplente, user=user)

    if request.method == 'POST':
        if form.is_valid():
            titulo = form.cleaned_data['titulo']
            mensagem = form.cleaned_data['mensagem']
            assinatura = form.cleaned_data['assinatura']
            enviado = inadimplente.send_email_cobranca(
                titulo,
                mensagem,
                assinatura
            )

            if enviado:
                msg = 'Email de cobrança enviado com sucesso!'
                messages.success(request, msg)
            return redirect(reverse('inadimplentes_list', kwargs={'escola_pk': escola.pk}))
        else:
            msg = 'Falha no envio do email!'
            messages.warning(request, msg)

    context = {}
    context['form'] = form
    context['escola'] = escola
    context['inadimplente'] = inadimplente
    context['tab_administracao'] = "active"
    context['tab_inadimplentes'] = "active"
    context['can_edit'] = is_diretor

    return render(request, 'comunicacao/email_cobranca.html', context)