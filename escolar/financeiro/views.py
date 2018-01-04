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
from escolar.financeiro.forms import ano_corrente, ContratoEscolaSearchForm
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
