# coding: utf-8
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from escolar.core.models import UserGrupos, User
from django.contrib.auth.models import Group

from datetime import date
from calendar import monthrange

from escolar.financeiro.models import ContratoAluno
from escolar.financeiro.forms import (
    ano_corrente,
    mes_corrnete,
    ContratoAlunoForm,
    ContratoAlunoSearchForm,
    PagamentoEscolaSearchForm,
    PagamentoAlunoEscolaSearchForm,
)

from escolar.escolas.models import Escola


@login_required
def responsaveis_list(request, escola_pk):
    '''
    ref #31
    **[[Todos]] Responaveis por Alunos / Escola
    '''
    user = request.user
    escola = get_object_or_404(Escola, pk=escola_pk)
    if not user.can_access_escola(escola_pk):
        raise Http404

    form = ContratoAlunoSearchForm(request.GET or None, escola=escola)
    if form.is_valid():
        contratos = form.get_result_queryset()
    else:
        contratos = form.get_result_queryset().filter(ano=ano_corrente)
    context = {}

    # ### PAGINAÇÃO ####
    get_copy = request.GET.copy()
    context['parameters'] = get_copy.pop('page', True) and get_copy.urlencode()
    page = request.GET.get('page', 1)
    paginator = Paginator(contratos, 15)
    try:
        contratos = paginator.page(page)
    except PageNotAnInteger:
        contratos = paginator.page(1)
    except EmptyPage:
        contratos = paginator.page(paginator.num_pages)
    # ### paginação ####

    can_edit = any([user.is_admin(), user.is_diretor(escola_pk)])
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
    **[[Todos]] Contratos de Alunos / Escola
    '''

    Aluno = apps.get_model(app_label='escolas', model_name='Aluno')
    user = request.user
    escola = get_object_or_404(Escola, pk=escola_pk)
    if not user.can_access_escola(escola.pk):
        raise Http404
    can_edit = any([user.is_admin(), user.is_diretor(escola.pk)])
    context = {}

    form = ContratoAlunoSearchForm(request.GET or None, escola=escola)  # ****
    if form.is_valid():
        contratos = form.get_result_queryset()
    else:
        contratos = form.get_result_queryset().filter(ano=ano_corrente)

    # ### PAGINAÇÃO ####
    get_copy = request.GET.copy()
    parameters = get_copy.pop('page', True) and get_copy.urlencode()
    page = request.GET.get('page', 1)
    paginator = Paginator(contratos, 15)
    try:
        contratos = paginator.page(page)
    except PageNotAnInteger:
        contratos = paginator.page(1)
    except EmptyPage:
        contratos = paginator.page(paginator.num_pages)
    context['parameters']= parameters
    # ### paginação ####

    context['form'] = form
    context['escola'] = escola
    context['can_edit'] = can_edit
    context['object_list'] = contratos

    # context['tab_alunos'] = "active"
    context['tab_contratos'] = "active"

    return render(request, 'financeiro/contratos_list.html', context)


@login_required
def contratos_aluno_list(request, aluno_pk):
    '''
    ref #34
    Lista todos os contratos do Aluno,
    na aba 'Contratos' do submenu de Aluno
    Não precisa de paginação
    do infantil ao 3 colegial, não mais que 15 linhas
    '''
    user = request.user
    Aluno = apps.get_model(app_label='escolas', model_name='Aluno')
    aluno = get_object_or_404(Aluno, pk=aluno_pk)
    escola = get_object_or_404(Escola, pk=aluno.escola.pk)
    if not user.can_access_escola(escola.pk):
        raise Http404
    can_edit = any([user.is_admin(), user.is_diretor(escola.pk)])
    page = request.GET.get('page', 1)

    contratos = ContratoAluno.objects.filter(aluno=aluno).order_by('-ano')
    
    context = {}
 
    context['escola'] = escola
    context['can_edit'] = can_edit
    context['object_list'] = contratos
    context['aluno'] = aluno

    context['tab_alunos'] = "active"
    context['tab_aluno_contratos'] = "active"

    return render(request, 'financeiro/contratos_aluno_list.html', context)


@login_required
def contrato_form(request, aluno_pk, contrato_pk=None):
    user = request.user
    Aluno = apps.get_model(app_label='escolas', model_name='Aluno')
    aluno = get_object_or_404(Aluno, pk=aluno_pk)
    escola = aluno.escola
    can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
    if not can_edit:
        raise Http404
    if not user.can_access_escola(escola.pk):
        raise Http404
    if contrato_pk:
        contrato = get_object_or_404(ContratoAluno, pk=contrato_pk)
        msg = u'Contrato alterado com sucesso.'
    else:
        contrato = None
        msg = u'Contrato criado.' 

    form = ContratoAlunoForm(request.POST or None, request.FILES or None, instance=contrato, aluno=aluno, user=user)
    context = {}
    context['form'] = form
    context['contrato'] = contrato
    context['aluno'] = aluno
    context['can_edit'] = can_edit
    context['escola'] = escola
    context['tab_alunos'] = "active"
    context['tab_aluno_contratos'] = "active"

    if request.method == 'POST':
        if form.is_valid():
            contrato = form.save()
            messages.success(request, msg)
            return redirect(reverse('contrato_cadastro', kwargs={'contrato_pk': contrato.pk}))
        else:
            messages.warning(request, u'Falha no cadastro do contrato.')

    return render(request, 'financeiro/contrato_form.html', context)


@login_required
def contrato_cadastro(request, contrato_pk):
    user = request.user

    contrato = get_object_or_404(ContratoAluno, pk=contrato_pk)
    escola = contrato.aluno.escola
    if not user.can_access_escola(escola.pk):
        raise Http404
    aluno = contrato.aluno
    can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
    context = {}
    context["escola"] = escola
    context["contrato"] = contrato
    context["aluno"] = aluno
    context['can_edit'] = can_edit
    context['tab_alunos'] = "active"
    context['tab_aluno_contratos'] = "active"
    return render(request, 'financeiro/contrato_cadastro.html', context)


@login_required
def pagamentos_aluno_list(request, aluno_pk):
    '''
    ref #35
    Todos Pgtos / Escola / Aluno
    '''
    user = request.user
    Aluno = apps.get_model(app_label='escolas', model_name='Aluno')
    aluno =  get_object_or_404(Aluno, pk=aluno_pk)
    escola = aluno.escola
    if not user.can_access_escola(escola.pk):
        raise Http404

    can_edit = any([user.is_admin(), user.is_diretor(escola.pk)])

    form = PagamentoAlunoEscolaSearchForm(request.GET or None, escola=escola, aluno=aluno)
    if form.is_valid():
        pagamentos = form.get_result_queryset()
    else:
        pagamentos = form.get_result_queryset().filter(contrato__ano=ano_corrente)
  
    context = {}
    context['form'] = form
    context['escola'] = escola
    context['aluno'] = aluno
    context['can_edit'] = can_edit
    context['object_list'] = pagamentos

    context['tab_alunos'] = "active"
    context['tab_pagamentos_aluno'] = "active"

    return render(request, 'financeiro/pagamentos_aluno_list.html', context)

@login_required
def pagamentos_list(request, escola_pk):
    '''
    ref #31
    Todos Pgtos e Recebimentos / Escola
    '''
    user = request.user
    can_edit = any([user.is_admin(), user.is_diretor(escola_pk)])
    escola = get_object_or_404(Escola, pk=escola_pk)
    if not user.can_access_escola(escola.pk):
        raise Http404
    context = {}

    form = PagamentoEscolaSearchForm(request.GET or None, escola=escola)
    if form.is_valid():
        pagamentos = form.get_result_queryset()
    else:
        data_ini = date(ano_corrente, mes_corrnete, 1)
        data_fim = date(ano_corrente, mes_corrnete, monthrange(ano_corrente, mes_corrnete)[1])
        pagamentos = form.get_result_queryset().filter(data_prevista__gte=data_ini,
                                                       data_prevista__lte=data_fim )
    # ### PAGINAÇÃO ####
    get_copy = request.GET.copy()
    context['parameters'] = get_copy.pop('page', True) and get_copy.urlencode()
    
    page = request.GET.get('page', 1)
    paginator = Paginator(pagamentos, 15)
    try:
        pagamentos = paginator.page(page)
    except PageNotAnInteger:
        pagamentos = paginator.page(1)
    except EmptyPage:
        pagamentos = paginator.page(paginator.num_pages)
    # ### paginação ####
    
    context['form'] = form
    context['escola'] = escola
    context['can_edit'] = can_edit
    context['object_list'] = pagamentos

    # context['tab_alunos'] = "active"
    context['tab_parcelas'] = "active"

    return render(request, 'financeiro/pagamentos_list.html', context)