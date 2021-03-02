# coding: utf-8
import json
import xlwt
from calendar import monthrange
from datetime import date, datetime
from decimal import Decimal
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.db.models import BooleanField, DateTimeField, Case, Value, When, Q, Sum
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from escolar.core.models import UserGrupos, User
from escolar.financeiro.models import (
    CategoriaPagamento,
    ContratoAluno,
    Bandeira,
    BandeiraEscolaParametro,
    InadimplenteDBView,
    Pagamento,
    ParametrosContrato,
)

from escolar.financeiro.forms import (
    ANO_CORRENTE,
    MES_CORRNETE,
    BandeiraEscolaParametroForm,
    BandeiraForm,
    CategoriaPagamentoForm,
    ContratoAlunoForm,
    ContratoAlunoSearchForm,
    InadimplentesSearchForm,
    PagamentoAlunoEscolaSearchForm,
    PagamentoEscolaSearchForm,
    PagamentoForm,
    ParametrosContratoForm,
)

from escolar.escolas.models import Escola

from escolar.escolas.forms import EmailRespensavelForm


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
        contratos = form.get_result_queryset().filter(ano=ANO_CORRENTE)
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
    if not user.is_diretor(escola.pk):
        raise Http404
    can_edit = any([user.is_admin(), user.is_diretor(escola.pk)])
    context = {}

    form = ContratoAlunoSearchForm(request.GET or None, escola=escola)  # ****
    if form.is_valid():
        contratos = form.get_result_queryset()
    else:
        contratos = form.get_result_queryset().filter(ano=ANO_CORRENTE)
    total = contratos.count()

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

    context['total'] = total
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
    if not user.is_diretor(escola.pk):
        raise Http404
    can_edit = any([user.is_admin(), user.is_diretor(escola.pk)])
    page = request.GET.get('page', 1)

    contratos = ContratoAluno.objects.filter(aluno=aluno).order_by('-ano')
    total = contratos.count()

    context = {}
    context['escola'] = escola
    context['can_edit'] = can_edit
    context['object_list'] = contratos
    context['aluno'] = aluno
    context['total'] = total
    context['tab_alunos'] = "active"
    context['tab_aluno_contratos'] = "active"

    return render(request, 'financeiro/contratos_aluno_list.html', context)


import cgi
import sys
 
def output(content):
    sys.stdout.write('Content-Type: text/plain\n\n')
    sys.stdout.write(content)
 

@login_required
def grafico_contratos_pagamentos(request, aluno_pk):
    user = request.user
    Aluno = apps.get_model(app_label='escolas', model_name='Aluno')
    aluno = get_object_or_404(Aluno, pk=aluno_pk)
    escola = get_object_or_404(Escola, pk=aluno.escola.pk)
    if not user.is_diretor(escola.pk):
        raise Http404
    can_edit = any([user.is_admin(), user.is_diretor(escola.pk)])
    page = request.GET.get('page', 1)

    contratos_ids = ContratoAluno.objects.filter(aluno=aluno).values_list('id')
    pagamentos = Pagamento.objects.filter(contrato__id__in=contratos_ids).order_by('data')

    context = {}
    context['escola'] = escola
    context['can_edit'] = can_edit

  
    pgtos = Pagamento.objects.get_pontualidade_pagamentos(aluno)

    object_list = [{'data': str(pg['data']), 'dia': pg['contrato__vencimento'], 'dia_real': pg['data'].day } for pg in pgtos]

    context['object_list'] = json.dumps(object_list)

    context['aluno'] = aluno
    context['tab_alunos'] = "active"
    context['tab_aluno_contratos'] = "active"

    return render(request, 'financeiro/grafico_contratos_pagamentos.html', context)


@login_required
def parametros_contrato_form(request, escola_pk, parametro_pk=None):
    user = request.user
    escola = get_object_or_404(Escola, pk=escola_pk)
    can_edit = user.is_diretor(escola.id)
    # no save do EscolaForm, já criou 1 parâmetro para Escola
    parametros = None
    if parametro_pk:
        parametros = escola.parametroscontrato_set.get(id=parametro_pk)
    if not can_edit:
        raise Http404

    msg = u'Parâmetros alterados com sucesso.'

    form = ParametrosContratoForm(request.POST or None, request.FILES or None, instance=parametros, escola=escola, user=user)
    context = {}
    context['form'] = form
    context['parametros'] = parametros
    context['escola'] = escola
    context['can_edit'] = can_edit

    context['tab_sistema'] = "active"
    context['tab_parametros'] = "active"

    if request.method == 'POST':
        if form.is_valid():
            parametros = form.save()
            messages.success(request, msg)
            return redirect(reverse('parametro_cadastro', kwargs={'escola_pk': escola.pk, 'parametro_pk': parametros.pk }))
        else:
            messages.warning(request, u'Falha na edição dos parâmetros.')

    return render(request, 'financeiro/parametros_contrato_form.html', context)


@login_required
def parametro_cadastro(request, escola_pk, parametro_pk):
    user = request.user

    escola = get_object_or_404(Escola, pk=escola_pk)
    if not user.can_access_escola(escola.pk):
        raise Http404
    parametros = escola.parametroscontrato_set.get(id=parametro_pk)
    can_edit = user.is_diretor(escola.id)
    context = {}
    context["escola"] = escola
    context["parametros"] = parametros

    context['can_edit'] = can_edit
    context['tab_sistema'] = "active"
    context['tab_parametros'] = "active"
    return render(request, 'financeiro/parametros_contrato_cadastro.html', context)


@login_required
def parametros_contrato_list(request, escola_pk):
    '''
    Lista os parametros cadastrados
    '''
    escola = None
    if escola_pk:
        escola = get_object_or_404(Escola, pk=escola_pk)
    user = request.user
    can_edit = user.is_diretor(escola.id)
    parametros = ParametrosContrato.objects.filter(escola=escola)
    can_create = parametros.count() < 2

    parametros = parametros.annotate(can_edit=Case(When(escola=escola, then=Value(True)), output_field=BooleanField()))

    context = {}
    context['object_list'] = parametros
    context['can_edit'] = can_edit
    context['can_create'] = can_create
    context['escola'] = escola
    context['tab_sistema'] = "active"
    context['tab_parametros'] = "active"
    return render(request, 'financeiro/parametros_contrato_list.html', context)

@login_required
def contrato_form(request, aluno_pk, contrato_pk=None):
    user = request.user
    Aluno = apps.get_model(app_label='escolas', model_name='Aluno')
    aluno = get_object_or_404(Aluno, pk=aluno_pk)
    escola = aluno.escola
    if not user.is_diretor(escola.pk):
        raise Http404
    if contrato_pk:
        contrato = get_object_or_404(ContratoAluno, pk=contrato_pk)
        msg = u'Contrato alterado com sucesso.'
    else:
        contrato = None
        msg = u'Contrato criado.' 
    can_edit = all([user.is_diretor(escola.id)])
    if not can_edit:
        raise Http404

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
    if not user.is_diretor(escola.pk):
        raise Http404
    aluno = contrato.aluno
    can_edit = all([user.is_diretor(escola.id)])
    context = {}
    context["escola"] = escola
    context["contrato"] = contrato
    context["aluno"] = aluno
    context['can_edit'] = can_edit
    context['tab_alunos'] = "active"
    context['tab_aluno_contratos'] = "active"
    return render(request, 'financeiro/contrato_cadastro.html', context)


@login_required
def contrato_impressao(request, contrato_pk):
    user = request.user

    contrato = get_object_or_404(ContratoAluno, pk=contrato_pk)
    escola = contrato.aluno.escola

    # responsável financeiro também terá acesso
    if not user.is_diretor(escola.pk):
        raise Http404
    aluno = contrato.aluno
    can_edit = user.is_diretor(escola.id)
    context = {}
    context["escola"] = escola
    context["contrato"] = contrato
    context["aluno"] = aluno
    context['can_edit'] = can_edit
    context['tab_alunos'] = "active"
    context['tab_aluno_contratos'] = "active"
    template = 'financeiro/contrato_%s.html' % escola.slug
    return render(request, template, context)


@login_required
def pagamento_form(request, escola_pk, contrato_pk=None, pagamento_pk=None):
    user = request.user
    Escola = apps.get_model(app_label='escolas', model_name='Escola')
    escola = get_object_or_404(Escola, pk=escola_pk)
    can_edit = user.is_diretor(escola.id)
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

    form = PagamentoForm(
        request.POST or None,
        request.FILES or None,
        instance=pagamento,
        escola=escola,
        contrato=contrato,
        user=user
    )

    if request.method == 'POST':
        if form.is_valid():
            pagamento = form.save()
            gerar_parcela = request.POST.get('gerar_complementar')
            efet = pagamento.efet
            if efet and gerar_parcela is not None:
                previsto = request.POST.get('valor_previsto')
                data = request.POST.get('data_parcela_adicional')
                valor = request.POST.get('parcela_adicional')
                obs = ' Parcela complementar gerada para: {0} no valor de: {1}'.format(data, valor)
                msg += obs
                obs += ' O valor previsto era de: R$ {0}'.format(previsto)
                pagamento.gerar_complementar(previsto, data, valor, obs)

            messages.success(request, msg)
            if contrato and not 'list' in str(request):
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

    # responsável financeiro terá acesso
    if not user.is_diretor(escola.pk):
        raise Http404
    contrato = pagamento.contrato.contratoaluno
    aluno = pagamento.contrato.contratoaluno.aluno
    resp_financeiro = pagamento.contrato.contratoaluno.responsavel
    form = EmailRespensavelForm(request.POST or None, instance=resp_financeiro)

    #  ## VERIFICA E MANDA EMAIL COM O RECIBO
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            if 'enviar_email_responsavel' in request.POST:
                enviado = pagamento.send_email_recibo(user)
                if enviado:
                    msg = 'Email enviado com sucesso!'
                    messages.success(request, msg)
        else:
            msg = 'Falha no envio do email!'
            messages.warning(request, msg)
    context = {}
    context['aluno'] = aluno
    context['form'] = form
    context['pagamento'] = pagamento
    context['escola'] = escola
    context['contrato'] = contrato
    context['data'] = date.today
    context['tab_alunos'] = "active"
    context['tab_pagamentos_aluno'] = "active"
    # print('=====================')
    # print(len(connection.queries))
    # print('=====================')
    return render(request, 'financeiro/recibo.html', context)


@login_required
def categoria_form(request, escola_pk, categoria_pk=None):
    user = request.user
    escola = get_object_or_404(Escola, pk=escola_pk)
    can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
    can_create = any([user.is_admin(), user.is_diretor(escola.id)]) and CategoriaPagamento.objects.filter(escola=escola).count() < 10

    if not user.can_access_escola(escola.pk):
        raise Http404
    if categoria_pk:
        categoria = get_object_or_404(CategoriaPagamento, pk=categoria_pk)
        msg = u'Categoria alterada com sucesso.'
    else:
        categoria = None
        msg = u'Categoria criada.' 

    if categoria_pk and not can_edit:
        raise Http404
    elif not categoria_pk and not can_create:
        raise Http404

    form = CategoriaPagamentoForm(request.POST or None, request.FILES or None, instance=categoria, escola=escola, user=user)

    if request.method == 'POST':
        if form.is_valid():
            categoria = form.save()
            messages.success(request, msg)
            return redirect(reverse('categorias_list', kwargs={'escola_pk': escola.pk}))
        else:
            messages.warning(request, u'Falha na edição dos parâmetros.')
    context = {}
    context['form'] = form
    context['categoria'] = categoria
    context['escola'] = escola
    context['can_edit'] = can_edit

    context['tab_sistema'] = "active"
    context['tab_categorias'] = "active"

    return render(request, 'financeiro/categoriapagamento_form.html', context)


@login_required
def categorias_list(request, escola_pk):
    '''
    Lista todas as categrias
    as básicas não são editáveis
    1º as suas
    '''
    escola = None
    if escola_pk:
        escola = get_object_or_404(Escola, pk=escola_pk)
    user = request.user
    can_edit = user.is_diretor(escola.id) and CategoriaPagamento.objects.filter(escola=escola).count() < 10
    categorias = CategoriaPagamento.objects.filter(Q(escola=None) | Q(escola=escola))

    categorias = categorias.annotate(can_edit=Case(When(escola=escola, then=Value(True)), output_field=BooleanField()))

    context = {}
    context['categorias'] = categorias
    context['can_edit'] = can_edit
    context['escola'] = escola
    context['tab_sistema'] = "active"
    context['tab_categorias'] = "active"
    return render(request, 'financeiro/categorias_list.html', context)


@login_required
def bandeira_form(request, escola_pk, bandeira_pk=None, parametros_pk=None):
    user = request.user
    escola = get_object_or_404(Escola, pk=escola_pk)
    can_edit = user.is_diretor(escola.id)
    can_create = user.is_diretor(escola.id)

    if not can_create:
        raise Http404
    if bandeira_pk:
        bandeira = get_object_or_404(Bandeira, pk=bandeira_pk)
        msg = u'bandeira alterada com sucesso.'
    else:
        bandeira = None
        msg = u'bandeira criada.'
    parametros = None
    if parametros_pk:
        parametros = get_object_or_404(BandeiraEscolaParametro, pk=parametros_pk)

    if bandeira_pk and not can_edit:
        raise Http404
    elif not bandeira_pk and not can_create:
        raise Http404

    form = BandeiraForm(request.POST or None, instance=bandeira, escola=escola, user=user)
    form_param = BandeiraEscolaParametroForm(request.POST or None, instance=parametros, escola=escola, bandeira=bandeira)

    if request.method == 'POST':
        if form.is_valid() and form_param.is_valid():
            bandeira = form.save()
            form_param.bandeira = bandeira
            form_param.save()
            messages.success(request, msg)
            return redirect(reverse('bandeiras_list', kwargs={'escola_pk': escola.pk}))
        else:
            messages.warning(request, u'Falha na edição dos parâmetros.')
    context = {}
    context['form'] = form
    context['form_param'] = form_param
    context['bandeira'] = bandeira
    context['escola'] = escola
    context['can_edit'] = can_edit

    context['tab_sistema'] = "active"
    context['tab_categorias'] = "active"

    return render(request, 'financeiro/bandeira_form.html', context)


@login_required
def bandeiras_list(request, escola_pk):
    '''
    Lista todas as bandeiras de cartões de recebimentos
    as básicas não são editáveis
    '''
    escola = get_object_or_404(Escola, pk=escola_pk)
    user = request.user
    can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
    bandeiras = Bandeira.objects.filter(Q(escola=None) | Q(escola=escola))

    bandeiras = bandeiras.annotate(can_edit=Case(When(escola=escola, then=Value(True)), output_field=BooleanField()))

    context = {}
    context['bandeiras'] = bandeiras
    context['can_edit'] = can_edit
    context['escola'] = escola
    context['tab_sistema'] = "active"
    context['tab_bandeiras'] = "active"
    return render(request, 'financeiro/bandeiras_list.html', context)

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
    is_diretor = user.is_diretor(escola.pk)
    contrato = ContratoAluno.objects.filter(aluno=aluno, ano=ANO_CORRENTE).last()

    # aqui o resp financeiro tb terá algum acesso
    if not is_diretor:
        raise Http404

    context = {}
    if contrato:
        can_edit = all([is_diretor, contrato, not contrato.rescindido])
    else:
        can_edit = all([is_diretor])

    form = PagamentoAlunoEscolaSearchForm(request.GET or None, escola=escola, aluno=aluno)

    data_fim = date(ANO_CORRENTE, MES_CORRNETE, monthrange(ANO_CORRENTE, MES_CORRNETE)[1])
    if form.is_valid():
        pagamentos = form.get_result_queryset()
    else:
        pagamentos = form.get_result_queryset().filter(contrato__ano=ANO_CORRENTE)

    hj = date.today()
    # pgtos atrasados
    # tem Juros e Multa
    pagamentos_qs = pagamentos.all().annotate(
                    atrasado=Case(
                        When(efet=False,
                             data__lte=hj,
                             categoria_id=1,
                             then=Value(True)), output_field=BooleanField()))

    pagamentos_qs = pagamentos_qs.all().annotate(
                    can_pay=Case(
                             When(efet=False,
                                  data__lte=data_fim,
                                  then=Value(True)), output_field=BooleanField()))
    # SE Contrato Rescindido
    pagamentos_qs = pagamentos_qs.all().annotate(
                    invalido=Case(
                             When(contrato__rescindido=True,
                                  efet=False,
                                  then=Value(True)), output_field=BooleanField()))

    pagamentos_qs = pagamentos_qs.all().filter(invalido=None)

 
    ano_valido = list(set(pagamentos_qs.values_list('contrato__ano', flat=True)))

    total_previsto = sum(pagamentos_qs.filter(tipo=1).values_list('valor', flat=True))
    total_realizado = sum(pagamentos_qs.filter(tipo=1, efet=True).values_list('valor', flat=True))


    # o pgto tem de estar vinculado a um contrato
    # o default para isso é o contrato do ano corrente,
    # pagamentos de novos contratos, tem funções do ContratoAluno, que geram todas as parcelas básicas do ano
    can_create = all([len(ano_valido) == 1, ano_valido[0] == ANO_CORRENTE, can_edit]) if ano_valido else False

    # ### PAGINAÇÃO ####
    get_copy = request.GET.copy()
    context['parameters'] = get_copy.pop('page', True) and get_copy.urlencode()
    
    page = request.GET.get('page', 1)

    paginator = Paginator(pagamentos_qs, 20)
    try:
        pagamentos = paginator.page(page)
    except PageNotAnInteger:
        pagamentos = paginator.page(1)
    except EmptyPage:
        pagamentos = paginator.page(paginator.num_pages)
    # ### paginação ####

    context['total_previsto'] = total_previsto
    context['total_realizado'] = total_realizado
    context['is_diretor'] = is_diretor

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
    is_diretor = user.is_diretor(escola.pk)
    if not is_diretor:
        raise Http404
    context = {}

    data_ini = date(ANO_CORRENTE, MES_CORRNETE, 1)
    data_fim = date(ANO_CORRENTE, MES_CORRNETE, monthrange(ANO_CORRENTE, MES_CORRNETE)[1])
    efet = ''
    form = PagamentoEscolaSearchForm(request.GET or None, escola=escola)
    if form.is_valid():
        pagamentos_qs = form.get_result_queryset()
        efet = form.cleaned_data['efet']
    else:
        pagamentos_qs = form.get_result_queryset().filter(
            data_pag__gte=data_ini, data_pag__lte=data_fim)

    hj = date.today()
    # pgtos atrasados
    # tem Juros e Multa
    pagamentos_qs = pagamentos_qs.all().annotate(
                    atrasado=Case(
                        When(efet=False,
                             data__lte=hj,
                             categoria_id=1,
                             then=Value(True)), output_field=BooleanField()))

    pagamentos_qs = pagamentos_qs.all().annotate(
                    can_pay=Case(
                         When(efet=False,
                              data__lte=data_fim,
                              then=Value(True)), output_field=BooleanField()))


    # SE Contrato Rescindido
    pagamentos_qs = pagamentos_qs.all().annotate(
                                invalido=Case(
                                    When(contrato__isnull=False,
                                         contrato__rescindido=True,
                                         efet=False,
                                         then=Value(True)), output_field=BooleanField()))

    pagamentos_qs = pagamentos_qs.all().filter(invalido=None)
    lancamentos = pagamentos_qs.count()
    pagamentos_ids = list(pagamentos_qs.values_list('id', flat=True))


    total_pos = sum(pagamentos_qs.filter(tipo=1).values_list('valor', flat=True))
    total_neg = sum(pagamentos_qs.filter(tipo=2).values_list('valor', flat=True))
    total = total_pos - total_neg
    entradas=int(total_pos)
    saidas=int(total_neg)

    entradas_real = sum(pagamentos_qs.filter(tipo=1, efet=True).values_list('valor', flat=True))
    saidas_real = sum(pagamentos_qs.filter(tipo=2, efet=True).values_list('valor', flat=True))
    total_real = entradas_real - entradas_real

    # ## gráfico Meios de pgto
    boleto_bancario = pagamentos_qs.filter(tipo=1, forma_pgto=1).aggregate(Sum('valor'))['valor__sum'] or 0
    cartao_credito = pagamentos_qs.filter(tipo=1, forma_pgto=2).aggregate(Sum('valor'))['valor__sum'] or 0
    cartao_debto = pagamentos_qs.filter(tipo=1, forma_pgto=3).aggregate(Sum('valor'))['valor__sum'] or 0
    cheque = pagamentos_qs.filter(tipo=1, forma_pgto=4).aggregate(Sum('valor'))['valor__sum'] or 0
    dinheiro = pagamentos_qs.filter(tipo=1, forma_pgto=5).aggregate(Sum('valor'))['valor__sum'] or 0
    permuta = pagamentos_qs.filter(tipo=1, forma_pgto=6).aggregate(Sum('valor'))['valor__sum'] or 0
    transf_bancaria = pagamentos_qs.filter(tipo=1, forma_pgto=7).aggregate(Sum('valor'))['valor__sum'] or 0
    indefinidos = pagamentos_qs.filter(tipo=1, forma_pgto=None).aggregate(Sum('valor'))['valor__sum'] or 0

    saidas_boleto_bancario = pagamentos_qs.filter(tipo=2, forma_pgto=1).aggregate(Sum('valor'))['valor__sum'] or 0
    saidas_cartao_credito = pagamentos_qs.filter(tipo=2, forma_pgto=2).aggregate(Sum('valor'))['valor__sum'] or 0
    saidas_cartao_debto = pagamentos_qs.filter(tipo=2, forma_pgto=3).aggregate(Sum('valor'))['valor__sum'] or 0
    saidas_cheque = pagamentos_qs.filter(tipo=2, forma_pgto=4).aggregate(Sum('valor'))['valor__sum'] or 0
    saidas_dinheiro = pagamentos_qs.filter(tipo=2, forma_pgto=5).aggregate(Sum('valor'))['valor__sum'] or 0
    saidas_permuta = pagamentos_qs.filter(tipo=2, forma_pgto=6).aggregate(Sum('valor'))['valor__sum'] or 0
    saidas_transf_bancaria = pagamentos_qs.filter(tipo=2, forma_pgto=7).aggregate(Sum('valor'))['valor__sum'] or 0
    saidas_indefinidos = pagamentos_qs.filter(tipo=2, forma_pgto=None).aggregate(Sum('valor'))['valor__sum'] or 0


    # ### PAGINAÇÃO ####
    get_copy = request.GET.copy()
    context['parameters'] = get_copy.pop('page', True) and get_copy.urlencode()
    page = request.GET.get('page', 1)

    paginator = Paginator(pagamentos_qs, 15)
    try:
        pagamentos = paginator.page(page)
    except PageNotAnInteger:
        pagamentos = paginator.page(1)
    except EmptyPage:
        pagamentos = paginator.page(paginator.num_pages)
    # ### paginação ####
    situacao = {'2': 'Previsto', '1': 'Pago', '0': 'Em Aberto', '': 'Previsto' }
    context['lancamentos'] = lancamentos
    context['total'] = total
    context['entradas'] = entradas
    context['saidas'] = saidas
    context['form'] = form
    context['escola'] = escola
    context['can_edit'] = can_edit
    context['object_list'] = pagamentos
    context['situacao'] = situacao[efet]

    ## grafico meios de pgto:
    context['boleto_bancario'] = int(boleto_bancario)
    context['cartao_credito'] = int(cartao_credito)
    context['cartao_debto'] = int(cartao_debto)
    context['cheque'] = int(cheque)
    context['dinheiro'] = int(dinheiro)
    context['permuta'] = int(permuta)
    context['transf_bancaria'] = int(transf_bancaria)
    context['indefinidos'] = int(indefinidos)
    context['is_diretor'] = is_diretor

    context['saidas_boleto_bancario'] = int(saidas_boleto_bancario)
    context['saidas_cartao_credito'] = int(saidas_cartao_credito)
    context['saidas_cartao_debto'] = int(saidas_cartao_debto)
    context['saidas_cheque'] = int(saidas_cheque)
    context['saidas_dinheiro'] = int(saidas_dinheiro)
    context['saidas_permuta'] = int(saidas_permuta)
    context['saidas_transf_bancaria'] = int(saidas_transf_bancaria)
    context['saidas_indefinidos'] = int(saidas_indefinidos)

    context['pagamentos_ids'] = pagamentos_ids
    context['tab_administracao'] = "active"
    context['tab_parcelas'] = "active"

    context['entradas_real'] = entradas_real
    context['saidas_real'] = saidas_real
    context['total_real'] = total_real

    return render(request, 'financeiro/pagamentos_list.html', context)


@login_required
def set_pagamento_status(request, pagamento_pk):
    '''
    ref #48 - ajax
    altera pagamento.efet
        para: True ou False
    '''
    meio_pgto = request.GET['meio_pgto']
    user = request.user
    data_hora = datetime.today()
    pagamento = get_object_or_404(Pagamento, id=pagamento_pk)
    escola = pagamento.escola
    can_edit = any([user.is_admin(), user.is_diretor(escola.pk)])
    observacao = ''
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
        observacao += '\n Marcado pago por: %s;\n em %s. \n O valor previsto era: R$ %s' % (user.nome, str(data_hora), valor_previsto)
        observacao += '\n Valor pago: R$ %s ' % pagamento.valor
        if multa:
            observacao += '\n Multa por atraso: R$ %s ' % multa
            observacao += '\n juros por atraso: R$ %s ' % juros
        pagamento.observacao = observacao
        pagamento.efet = True
        if meio_pgto:
            pagamento.forma_pgto = int(meio_pgto)
        pagamento.save()
        # GUARDA no HISTORICO:
        if pagamento.contrato:
            AlunoHistorico = apps.get_model('escolas', 'AlunoHistorico')
            historico = AlunoHistorico()
            historico.aluno = pagamento.contrato.contratoaluno.aluno
            historico.descricao = 'Pagamento: %s  | ' % pagamento.titulo
            historico.descricao += observacao
            historico.usuario = user
            historico.save()

    return HttpResponse('Ok')


@login_required
def inadimplentes_list(request, escola_pk):
    '''
    #2 github
    Todos devedores por dívida/ Escola
    '''
    user = request.user
    can_edit = any([user.is_admin(), user.is_diretor(escola_pk)])
    escola = get_object_or_404(Escola, pk=escola_pk)
    is_diretor = user.is_diretor(escola.pk)
    if not is_diretor:
        raise Http404
    context = {}

    data_ini = date(ANO_CORRENTE, 1, 1)
    data_fim = date(
        ANO_CORRENTE,
        MES_CORRNETE,
        monthrange(ANO_CORRENTE, MES_CORRNETE)[1]
    )

    form = InadimplentesSearchForm(request.GET or None, escola=escola)
    if form.is_valid():
        pagamentos = form.get_result_queryset()
    else:
        pagamentos = form.get_result_queryset()
    efet = '0'

    hj = date.today()

    pagamentos_ids = list(pagamentos.values_list('id', flat=True))
    lancamentos = pagamentos.count()

    total = pagamentos.aggregate(Sum('valor'))['valor__sum'] or 0
    multa = pagamentos.aggregate(Sum('multa'))['multa__sum'] or 0
    juros = pagamentos.aggregate(Sum('juros'))['juros__sum'] or 0
    tatal_final = total + multa + juros

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
    situacao = {'2': 'Previsto', '1': 'Pago', '0': 'Em Aberto', '': 'Previsto' }
    context['lancamentos'] = lancamentos
    context['total'] = total
    context['multa'] = multa
    context['juros'] = juros
    context['tatal_final'] = tatal_final
    context['form'] = form
    context['escola'] = escola
    context['can_edit'] = can_edit
    context['object_list'] = pagamentos
    context['situacao'] = situacao[efet]
    context['pagamentos_ids'] = pagamentos_ids

    context['tab_administracao'] = "active"
    context['tab_inadimplentes'] = "active"

    return render(request, 'financeiro/inadimplentes_list.html', context)


@login_required
def set_contrato_assinado(request, contrato_pk):
    '''
    ref #85 - ajax
    altera contrato.assinado
        para: True
    '''
    user = request.user
    data_hora = datetime.today()
    contrato = get_object_or_404(ContratoAluno, id=contrato_pk)
    escola = contrato.aluno.escola
    can_edit = any([user.is_admin(), user.is_diretor(escola.pk)])
    observacao = ''
    if not can_edit:
        raise Http404
    if contrato.assinado is True:
        contrato.assinado = False
    else:
        contrato.assinado = True
        observacao += '\n Marcado assinado por: %s;\n em %s. \n' % (user.nome, str(data_hora))
        contrato.observacao = observacao
        contrato.save()
        # GUARDA no HISTORICO:
        if contrato:
            AlunoHistorico = apps.get_model('escolas', 'AlunoHistorico')
            historico = AlunoHistorico()
            historico.aluno = contrato.aluno
            historico.descricao = 'Contrato: %s  | ' % observacao
            historico.usuario = user
            historico.save()

    return HttpResponse('Ok')


def pagamentos_gera_xls(request):
    '''
    ref #91
    '''
    pagamentos_ids = request.GET['pagamentos_ids']
    pagamentos_ids = pagamentos_ids.replace('[', '')
    pagamentos_ids = pagamentos_ids.replace(']', '')
    pagamentos_ids = pagamentos_ids.replace(',', '')
    pagamentos_ids =[int(i) for i in pagamentos_ids.split()]
    pagamentos = Pagamento.objects.filter(id__in=pagamentos_ids).order_by('data')

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=relatorio-pagamentos.xls'

    book = xlwt.Workbook(encoding='utf8')
    sheet = book.add_sheet('untitled')
    default_style = xlwt.Style.default_style
    title_style = xlwt.easyxf('font: bold 1')
    monetary_style = xlwt.easyxf(num_format_str='$#,##0.00')

    # campos
    values_list = [["Data",
                    "Tipo",
                    "Valor",
                    "Categoria",
                    "Resposável",
                    "CPF resp.",
                    "Forma de pagamento"]]

    for pagamento in pagamentos:
        data = str(pagamento.data)
        categoria = pagamento.categoria.nome if pagamento.categoria else ''
        responsavel = pagamento.contrato.contratoaluno.responsavel.nome if pagamento.contrato and pagamento.contrato.contratoaluno else ''
        cpf_resp = pagamento.contrato.contratoaluno.responsavel.cpf if pagamento.contrato and pagamento.contrato.contratoaluno else ''
        valor = pagamento.get_valor_liquido() if pagamento.taxa_cartao else pagamento.valor
        values_list.append([data,
                            pagamento.get_tipo_display(),
                            valor,
                            categoria,
                            responsavel,
                            cpf_resp,
                            pagamento.get_forma_pgto_display(),
                            ])
    for row, rowdata in enumerate(values_list):
        for col, val in enumerate(rowdata):
            if isinstance(val, Decimal):
                style = monetary_style
            else:
                style = default_style
            if row == 0:
                style = title_style

            sheet.write(row, col, val, style=style)

    book.save(response)
    return response


def inadimplentes_gera_xls(request):
    '''
    ref Github #3
    '''
    pagamentos_ids = request.GET['pagamentos_ids']
    pagamentos_ids = pagamentos_ids.replace('[', '')
    pagamentos_ids = pagamentos_ids.replace(']', '')
    pagamentos_ids = pagamentos_ids.replace(',', '')
    pagamentos_ids =[int(i) for i in pagamentos_ids.split()]
    pagamentos = InadimplenteDBView.objects.filter(id__in=pagamentos_ids)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    hoje = str(date.today())
    doc_nome = 'attachment; filename= %s-inadimplentes.xls' % hoje
    response['Content-Disposition'] = doc_nome

    book = xlwt.Workbook(encoding='utf8')
    sheet = book.add_sheet('untitled')
    default_style = xlwt.Style.default_style
    title_style = xlwt.easyxf('font: bold 1')
    monetary_style = xlwt.easyxf(num_format_str='$#,##0.00')

    # campos
    values_list = [["Nome Resp",
                    "CPF",
                    "Série",
                    "Nome Aluno",
                    "Celular",
                    "email",
                    "Ano",
                    "Pgtos Atrasdos",
                    "titulos",
                    "Valor",
                    "Multa",
                    "Juros",
                    "Total"]]

    for pagamento in pagamentos:
        responsavel_nome = pagamento.responsavel_nome
        cpf_resp_fin = pagamento.cpf_resp_fin or ''
        serie = pagamento.serie.serie
        aluno_nome = pagamento.aluno_nome
        celular = pagamento.celular or ''
        email = pagamento.email or ''
        ano = pagamento.ano
        pagamentos_atrasados = pagamento.pagamentos_atrasados
        titulos = " ".join(titulo for titulo in pagamento.titulos)
        valor = pagamento.valor or 0
        multa = pagamento.multa or 0
        juros = pagamento.juros or 0
        total = valor + multa + juros 

        values_list.append([responsavel_nome,
                            cpf_resp_fin,
                            serie,
                            aluno_nome,
                            celular,
                            email,
                            ano,
                            pagamentos_atrasados,
                            titulos,
                            valor,
                            juros,
                            multa,
                            total
                            ])
    for row, rowdata in enumerate(values_list):
        for col, val in enumerate(rowdata):
            if isinstance(val, Decimal):
                style = monetary_style
            else:
                style = default_style
            if row == 0:
                style = title_style

            sheet.write(row, col, val, style=style)

    book.save(response)
    return response
