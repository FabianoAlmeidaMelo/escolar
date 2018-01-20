# coding: utf-8
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from escolar.core.models import UserGrupos, User
from django.contrib.auth.models import Group

from datetime import date

from escolar.financeiro.models import ContratoEscola
from escolar.financeiro.forms import (
    ano_corrente,
    ContratoEscolaSearchForm,
    MovimentoEscolaSearchForm,
)

from escolar.escolas.models import Escola


@login_required
def responsaveis_list(request, escola_pk):
    '''
    ref #31
    Todos Responaveeis por Alunos / Escola
    '''
    user = request.user
    escola = get_object_or_404(Escola, pk=escola_pk)
    page = request.GET.get('page', 1)

    form = ContratoEscolaSearchForm(request.GET or None, escola=escola)
    if form.is_valid():
        contratos = form.get_result_queryset()
    else:
        contratos = form.get_result_queryset().filter(ano=ano_corrente)

    paginator = Paginator(contratos, 15)
    try:
        contratos = paginator.page(page)
    except PageNotAnInteger:
        contratos = paginator.page(1)
    except EmptyPage:
        contratos = paginator.page(paginator.num_pages)

    can_edit = any([user.is_admin(), user.is_diretor(escola_pk)])
    context = {}
    context['form'] = form
    context['escola'] = escola
    context['can_edit'] = can_edit
    context['object_list'] = contratos

    # context['tab_alunos'] = "active"
    context['tab_responsaveis'] = "active"

    return render(request, 'financeiro/responsaveis_list.html', context)


@login_required
def contratos_list(request, escola_pk):
    '''
    ref #31
    Todos Responaveeis por Alunos / Escola
    '''
    user = request.user
    can_edit = any([user.is_admin(), user.is_diretor(escola_pk)])
    escola = get_object_or_404(Escola, pk=escola_pk)
    page = request.GET.get('page', 1)

    form = ContratoEscolaSearchForm(request.GET or None, escola=escola)
    if form.is_valid():
        contratos = form.get_result_queryset()
    else:
        contratos = form.get_result_queryset().filter(ano=ano_corrente)

    paginator = Paginator(contratos, 15)
    try:
        contratos = paginator.page(page)
    except PageNotAnInteger:
        contratos = paginator.page(1)
    except EmptyPage:
        contratos = paginator.page(paginator.num_pages)
    
    context = {}
    context['form'] = form
    context['escola'] = escola
    context['can_edit'] = can_edit
    context['object_list'] = contratos

    # context['tab_alunos'] = "active"
    context['tab_contratos'] = "active"

    return render(request, 'financeiro/contratos_list.html', context)


@login_required
def contrato_cadastro(request, contrato_pk):
    user = request.user
    contrato = get_object_or_404(ContratoEscola, pk=contrato_pk)
    escola = contrato.escola
    can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
    context = {}
    context["escola"] = escola
    context["contrato"] = contrato
    context['can_edit'] = can_edit
    context['tab_contratos'] = "active"
    return render(request, 'financeiro/contrato_cadastro.html', context)


@login_required
def movimentos_list(request, escola_pk):
    '''
    ref #31
    Todos Pgtos e Recebimentos / Escola
    '''
    user = request.user
    can_edit = any([user.is_admin(), user.is_diretor(escola_pk)])
    escola = get_object_or_404(Escola, pk=escola_pk)
    page = request.GET.get('page', 1)

    form = MovimentoEscolaSearchForm(request.GET or None, escola=escola)
    if form.is_valid():
        pagamentos = form.get_result_queryset()
    else:
        pagamentos = form.get_result_queryset().filter(contrato__ano=ano_corrente)

    paginator = Paginator(pagamentos, 15)
    try:
        pagamentos = paginator.page(page)
    except PageNotAnInteger:
        pagamentos = paginator.page(1)
    except EmptyPage:
        pagamentos = paginator.page(paginator.num_pages)
    
    context = {}
    context['form'] = form
    context['escola'] = escola
    context['can_edit'] = can_edit
    context['object_list'] = pagamentos

    # context['tab_alunos'] = "active"
    context['tab_parcelas'] = "active"

    return render(request, 'financeiro/pagamentos_list.html', context)