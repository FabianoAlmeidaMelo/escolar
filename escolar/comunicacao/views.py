# coding: utf-8
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
    resolve_url,
)
from escolar.comunicacao.models import(
    MensagemDefault,
    PessoaMensagem
)
from escolar.comunicacao.forms import (
    MensagemDefaultForm,
)
from escolar.escolas.models import (
    Escola,
)
from escolar.financeiro.forms import (
    CobrancaMensagemForm,
)
from escolar.financeiro.models import (
    ContratoAluno,
    InadimplenteDBView
)

@login_required
def msg_default_form(request, escola_pk, msg_pk=None):
    user = request.user
    escola = get_object_or_404(Escola, pk=escola_pk)

    is_diretor = user.is_diretor(escola.pk)
    if not is_diretor:
        raise Http404
    tipo = None
    if msg_pk:
        msg_default = get_object_or_404(MensagemDefault, pk=msg_pk)
        tipo = msg_default.get_tipo_display()
        msg = u'Mensagem alterada com sucesso.'
    else:
        msg_default = None
        msg = u'Mensagem criada.'

    form = MensagemDefaultForm(
        request.POST or None,
        instance=msg_default,
        user=user,
        escola=escola
    )

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(reverse('msg_default_list', kwargs={'escola_pk': escola.pk}))
        else:
            messages.warning(request, u'Falha na edição da Mensagem.')

    context = {}
    context['form'] = form
    context['escola'] = escola
    context['tipo'] = tipo
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
def msg_list(request, escola_pk, contrato_id, tipo=None):
    '''
    Lista as Mensagens de cobrança a partir do Cobrado
    '''
    escola = get_object_or_404(Escola, pk=escola_pk)
    user = request.user
    can_edit = user.is_diretor(escola.id)
    if tipo:
        msg_qs = PessoaMensagem.objects.filter(
            mensagem__escola=escola,
            contrato_id=contrato_id,
            tipo=tipo
        )
    else:
        msg_qs = PessoaMensagem.objects.filter(
            mensagem__escola=escola,
            contrato_id=contrato_id
        )
    contrato = ContratoAluno.objects.get(
        id=contrato_id
    )
    context = {}
    context['msg_qs'] = msg_qs.order_by('-mensagem__data')
    context['can_edit'] = can_edit
    context['contrato'] = contrato
    context['escola'] = escola
    context['tab_administracao'] = "active"
    context['tab_inadimplentes'] = "active"
    return render(request, 'comunicacao/msg_list.html', context)


@login_required
def cobranca_mensagem_form(request, pk):
    user = request.user
    inadimplente = get_object_or_404(
        InadimplenteDBView,
        pk=pk
    )
    escola = inadimplente.escola
    is_diretor = user.is_diretor(escola.pk)
    if not is_diretor:
        raise Http404

    form = CobrancaMensagemForm(
        request.POST or None,
        instance=inadimplente,
        user=user,
        escola=escola
    )

    if request.method == 'POST':
        if form.is_valid():
            mensagem = form.cleaned_data['mensagem']
            enviado = inadimplente.send_email_cobranca(
                mensagem,
            )

            if enviado:
                msg = 'Email de cobrança enviado com sucesso!'
                inadimplente.set_mensagem_cobranca(mensagem, user)
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

    return render(request, 'comunicacao/cobranca_mensagem_form.html', context)
