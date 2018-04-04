# coding: utf-8
from calendar import monthrange
from datetime import date, datetime
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import BooleanField, Case, Value, When
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from escolar.core.models import UserGrupos, User

from escolar.financeiro.models import (
    ContratoAluno,
    Pagamento,
    ParametrosContrato,
)

from escolar.financeiro.forms import (
    ano_corrente,
    mes_corrnete,
    ContratoAlunoForm,
    ContratoAlunoSearchForm,
    PagamentoAlunoEscolaSearchForm,
    PagamentoEscolaSearchForm,
    PagamentoForm,
    ParametrosContratoForm,
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

    context['tab_administracao'] = "active"
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
def parametros_contrato_form(request, escola_pk):
    user = request.user
    escola = get_object_or_404(Escola, pk=escola_pk)
    can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
    # no save do EscolaForm, já criou 1 parâmetro para Escola
    parametros = escola.parametroscontrato_set.last()
    if not can_edit:
        raise Http404

    msg = u'Parâmetros alterados com sucesso.'

    form = ParametrosContratoForm(request.POST or None, request.FILES or None, instance=parametros, escola=escola, user=user)
    context = {}
    context['form'] = form
    context['parametros'] = parametros
    context['escola'] = escola
    context['can_edit'] = can_edit

    context['tab_administracao'] = "active"
    context['tab_parametros'] = "active"

    if request.method == 'POST':
        if form.is_valid():
            contrato = form.save()
            messages.success(request, msg)
            return redirect(reverse('parametro_cadastro', kwargs={'escola_pk': escola.pk}))
        else:
            messages.warning(request, u'Falha na edição dos parâmetros.')

    return render(request, 'financeiro/parametros_contrato_form.html', context)



@login_required
def parametro_cadastro(request, escola_pk):
    user = request.user

    escola = get_object_or_404(Escola, pk=escola_pk)
    if not user.can_access_escola(escola.pk):
        raise Http404
    parametros = escola.parametroscontrato_set.last()
    can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
    context = {}
    context["escola"] = escola
    context["parametros"] = parametros

    context['can_edit'] = can_edit
    context['tab_administracao'] = "active"
    context['tab_parametros'] = "active"
    return render(request, 'financeiro/parametros_contrato_cadastro.html', context)


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
def pagamento_form(request, escola_pk, contrato_pk=None, pagamento_pk=None):
    user = request.user
    Escola = apps.get_model(app_label='escolas', model_name='Escola')
    escola = get_object_or_404(Escola, pk=escola_pk)
    can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
    contrato = None
    aluno = None
    if contrato_pk:
        contrato = get_object_or_404(ContratoAluno, pk=contrato_pk)
        aluno = contrato.aluno

    if not can_edit:
        raise Http404
    if pagamento_pk:
        pagamento = get_object_or_404(Pagamento, pk=pagamento_pk)
        msg = u'Pagamento alterado com sucesso.'
        contrato = pagamento.contrato
        if contrato:
            aluno = contrato.contratoaluno.aluno
    else:
        pagamento = None
        msg = u'Pagamento criado.' 

    form = PagamentoForm(request.POST or None, request.FILES or None, instance=pagamento, escola=escola, contrato=contrato, user=user)

    if request.method == 'POST':
        if form.is_valid():
            pagamento = form.save()
            messages.success(request, msg)
            if contrato:
                return redirect(reverse('pagamentos_aluno_list', kwargs={'aluno_pk': aluno.pk}))
            else:
                return redirect(reverse('pagamentos_list', kwargs={'escola_pk': escola.pk}))
        else:
            messages.warning(request, u'Falha no cadastro do pagamento.')

    context = {}
    context['form'] = form
    context['pagamento'] = pagamento
    context['contrato'] = contrato
    context['aluno'] = aluno
    context['can_edit'] = can_edit
    context['escola'] = escola
    if contrato:
        context['tab_alunos'] = "active"
        context['tab_pagamentos_aluno'] = "active"
    else:
        context['tab_parcelas'] = "active"

    return render(request, 'financeiro/pagamento_form.html', context)


@login_required
def print_recibo(request, pagamento_pk):
    # from django.db import connection
    # pagamento = get_object_or_404(Pagamento, pk=pagamento_pk)
    user = request.user
    pagamento = Pagamento.objects.select_related('escola',
                                                 'contrato__contratoaluno',
                                                 'contrato__contratoaluno__aluno',
                                                 'contrato__contratoaluno__responsavel').filter(pk=pagamento_pk).last()
    escola = pagamento.escola
    if not user.can_access_escola(escola.pk):
        raise Http404
    contrato = pagamento.contrato.contratoaluno
    aluno = pagamento.contrato.contratoaluno.aluno
    context = {}
    context['aluno'] = aluno
    context['pagamento'] = pagamento
    context['escola'] = escola
    context['contrato'] = contrato
    context['data'] = date.today
    # print('=====================')
    # print(len(connection.queries))
    # print('=====================')
    return render(request, 'financeiro/recibo.html', context)


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
    contrato = ContratoAluno.objects.filter(aluno=aluno, ano=ano_corrente).last()
    if not user.can_access_escola(escola.pk):
        raise Http404

    context = {}

    can_edit = any([user.is_admin(), user.is_diretor(escola.pk)])

    form = PagamentoAlunoEscolaSearchForm(request.GET or None, escola=escola, aluno=aluno)
    
    if form.is_valid():
        pagamentos = form.get_result_queryset()
    else:
        pagamentos = form.get_result_queryset().filter(contrato__ano=ano_corrente)

    hj = date.today()
    # pgtos atrasados
    # tem Juros e Multa
    pagamentos = pagamentos.all().annotate(
                    atrasado=Case(
                        When(efet=False,
                             data__lte=hj,
                             categoria_id=1,
                             then=Value(True)), output_field=BooleanField()))
 
    ano_valido = list(set(pagamentos.values_list('contrato__ano', flat=True)))

    # o pgto tem de estar vinculado a um contrato
    # o default para isso é o contrato do ano corrente,
    # pagamentos de novos contratos, tem funções do ContratoAluno, que geram todas as parcelas básicas do ano
    can_create = all([len(ano_valido) == 1, ano_valido[0] == ano_corrente, can_edit]) if ano_valido else False

    # ### PAGINAÇÃO ####
    get_copy = request.GET.copy()
    context['parameters'] = get_copy.pop('page', True) and get_copy.urlencode()
    
    page = request.GET.get('page', 1)
    paginator = Paginator(pagamentos, 20)
    try:
        pagamentos = paginator.page(page)
    except PageNotAnInteger:
        pagamentos = paginator.page(1)
    except EmptyPage:
        pagamentos = paginator.page(paginator.num_pages)
    # ### paginação ####


    context['form'] = form
    context['can_create'] = can_create
    context['escola'] = escola
    context['aluno'] = aluno
    context['can_edit'] = can_edit
    context['object_list'] = pagamentos
    context['contrato'] = contrato
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
        pagamentos = form.get_result_queryset().filter(data__gte=data_ini,
                                                       data__lte=data_fim )

    hj = date.today()
    # pgtos atrasados
    # tem Juros e Multa
    pagamentos = pagamentos.all().annotate(
                    atrasado=Case(
                        When(efet=False,
                             data__lte=hj,
                             categoria_id=1,
                             then=Value(True)), output_field=BooleanField()))
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

    context['tab_administracao'] = "active"
    context['tab_parcelas'] = "active"

    return render(request, 'financeiro/pagamentos_list.html', context)


@login_required
def set_pagamento_status(request, pagamento_pk):
    '''
    ref #48 - ajax
    altera pagamento.efet
        para: True ou False
    '''
    user = request.user
    data_hora = datetime.today()
    pagamento = get_object_or_404(Pagamento, id=pagamento_pk)
    escola = pagamento.escola
    can_edit = any([user.is_admin(), user.is_diretor(escola.pk)])
    if not can_edit:
        raise Http404
    if pagamento.efet is True:
        pagamento.efet = False
    else:
        valor_previsto = pagamento.valor
        pagamento.valor = pagamento.get_valor_a_pagar() # Entra juros e multa se houver
        pagamento.data_pag = data_hora
        multa = ''
        juros = ''
        if pagamento.get_multa():
            multa = pagamento.get_multa()
            juros = pagamento.get_juros()
        pagamento.observacao += '\n Marcado pago por: %s;\n em %s. \n O valor previsto era: R$ %s' % (user.nome, str(data_hora), valor_previsto)
        pagamento.observacao += '\n Valor pago: R$ %s ' % pagamento.valor
        if multa:
            pagamento.observacao += '\n Multa por atraso: R$ %s ' % multa
            pagamento.observacao += '\n juros por atraso: R$ %s ' % juros
        pagamento.efet = True
    pagamento.save()

    return HttpResponse('Ok')