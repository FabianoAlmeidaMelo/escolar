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
from escolar.financeiro.forms import (
    EmailMensagemForm
)

from escolar.financeiro.models import (
    InadimplenteDBView,
 )

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