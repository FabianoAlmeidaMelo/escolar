# coding: utf-8
import xlwt
from calendar import monthrange
from datetime import date, datetime
from decimal import Decimal
from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import BooleanField, Case, Value, When, Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from escolar.core.models import UserGrupos, User
from escolar.financeiro.models import (
    CategoriaPagamento,
    ContratoAluno,
    Pagamento,
    ParametrosContrato,
)

from escolar.financeiro.forms import (
    ano_corrente,
    mes_corrnete,
    CategoriaPagamentoForm,
    ContratoAlunoForm,
    ContratoAlunoSearchForm,
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

    context['tab_sistema'] = "active"
    context['tab_parametros'] = "active"

    if request.method == 'POST':
        if form.is_valid():
            parametros = form.save()
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
    context['tab_sistema'] = "active"
    context['tab_parametros'] = "active"
    return render(request, 'financeiro/parametros_contrato_cadastro.html', context)


@login_required
def contrato_form(request, aluno_pk, contrato_pk=None):
    user = request.user
    Aluno = apps.get_model(app_label='escolas', model_name='Aluno')
    aluno = get_object_or_404(Aluno, pk=aluno_pk)
    escola = aluno.escola
    if not user.can_access_escola(escola.pk):
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
    if not user.can_access_escola(escola.pk):
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
    can_edit = any([user.is_admin(), user.is_diretor(escola.id)]) and CategoriaPagamento.objects.filter(escola=escola).count() < 10
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
    if contrato:
        can_edit = all([user.is_diretor(escola.pk), contrato, not contrato.rescindido])
    else:
        can_edit = all([user.is_diretor(escola.pk)])

    form = PagamentoAlunoEscolaSearchForm(request.GET or None, escola=escola, aluno=aluno)

    data_fim = date(ano_corrente, mes_corrnete, monthrange(ano_corrente, mes_corrnete)[1])
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

    pagamentos = pagamentos.all().annotate(
                    can_pay=Case(
                             When(efet=False,
                                  data__lte=data_fim,
                                  then=Value(True)), output_field=BooleanField()))
    # SE Contrato Rescindido
    pagamentos = pagamentos.all().annotate(
                    invalido=Case(
                             When(contrato__rescindido=True,
                                  efet=False,
                                  then=Value(True)), output_field=BooleanField()))

    pagamentos = pagamentos.all().filter(invalido=None)

 
    ano_valido = list(set(pagamentos.values_list('contrato__ano', flat=True)))

    total_pos = sum(pagamentos.filter(tipo=1).values_list('valor', flat=True))
    total_neg = sum(pagamentos.filter(tipo=2).values_list('valor', flat=True))
    total = total_pos - total_neg
    entradas = int(total_pos)
    saidas = int(total_neg)

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

    context['total'] = total
    context['entradas'] = entradas
    context['saidas'] = saidas
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

    data_ini = date(ano_corrente, mes_corrnete, 1)
    data_fim = date(ano_corrente, mes_corrnete, monthrange(ano_corrente, mes_corrnete)[1])

    form = PagamentoEscolaSearchForm(request.GET or None, escola=escola)
    if form.is_valid():
        pagamentos = form.get_result_queryset()
    else:
        pagamentos = form.get_result_queryset().filter(data__gte=data_ini,
                                                       data__lte=data_fim )
        # import pdb; pdb.set_trace()
    hj = date.today()
    # pgtos atrasados
    # tem Juros e Multa
    pagamentos = pagamentos.all().annotate(
                    atrasado=Case(
                        When(efet=False,
                             data__lte=hj,
                             categoria_id=1,
                             then=Value(True)), output_field=BooleanField()))

    pagamentos = pagamentos.all().annotate(
                    can_pay=Case(
                         When(efet=False,
                              data__lte=data_fim,
                              then=Value(True)), output_field=BooleanField()))


    # SE Contrato Rescindido
    pagamentos = pagamentos.all().annotate(
                                invalido=Case(
                                    When(contrato__isnull=False,
                                         contrato__rescindido=True,
                                         efet=False,
                                         then=Value(True)), output_field=BooleanField()))

    pagamentos = pagamentos.all().filter(invalido=None)
    pagamentos_ids = list(pagamentos.values_list('id', flat=True))


    total_pos = sum(pagamentos.filter(tipo=1).values_list('valor', flat=True))
    total_neg = sum(pagamentos.filter(tipo=2).values_list('valor', flat=True))
    total = total_pos - total_neg
    entradas=int(total_pos)
    saidas=int(total_neg)

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

    context['total'] = total
    context['entradas'] = entradas
    context['saidas'] = saidas
    context['form'] = form
    context['escola'] = escola
    context['can_edit'] = can_edit
    context['object_list'] = pagamentos
    context['pagamentos_ids'] = pagamentos_ids
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
        values_list.append([data,
                            pagamento.get_tipo_display(),
                            pagamento.valor,
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

