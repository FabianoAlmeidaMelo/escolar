# coding: utf-8
from datetime import date
from calendar import monthrange

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.db.models import BooleanField, Case, Value, When, Q, Sum

from escolar.core.models import Perfil, Endereco, User, UserGrupos
from escolar.core.forms import (
    EnderecoForm,
    GrupoForm,
    PerfilForm,
    PerfilSearchForm,
    UserForm,
    UserSearchForm,
)

from escolar.escolas.models import Escola
from escolar.financeiro.models import Pagamento
from escolar.financeiro.forms import (
    ANO_CORRENTE,
    MES_CORRNETE,
    )

def home(request, escola_pk=None):
    '''
    Se o user tem vínculo com uma escola e
    é do Grupo Diretor, a HOME mostra os Gráficos financeiros.

    '''
    user = request.user
    context = {}
    escola = None
    context['diretor'] = False
    if user.is_authenticated() and not escola_pk:
        escola_pk = user.get_unica_escola()
    if escola_pk:
        escola = get_object_or_404(Escola, pk=escola_pk)
        context['escola'] = escola
        context['diretor'] = user.is_admin() or user.is_diretor(escola_pk)

    data_ini = date(ANO_CORRENTE, MES_CORRNETE, 1)
    data_fim = date(ANO_CORRENTE, MES_CORRNETE, monthrange(ANO_CORRENTE, MES_CORRNETE)[1]) 
    pagamentos = Pagamento.objects.filter(escola=escola,
                                          data__gte=data_ini,
                                          data__lte=data_fim)


    # SE Contrato Rescindido
    pagamentos = pagamentos.all().annotate(
                                invalido=Case(
                                    When(contrato__isnull=False,
                                         contrato__rescindido=True,
                                         efet=False,
                                         then=Value(True)), output_field=BooleanField()))

    pagamentos = pagamentos.all().filter(invalido=None)
    lancamentos = pagamentos.count()
    pagamentos_ids = list(pagamentos.values_list('id', flat=True))


    total_pos = pagamentos.filter(tipo=1).aggregate(Sum('valor'))['valor__sum'] or 0
    total_neg = pagamentos.filter(tipo=2).aggregate(Sum('valor'))['valor__sum'] or 0
    total = total_pos - total_neg
    entradas=int(total_pos)
    saidas=int(total_neg)

    # ## gráfico Meios de pgto
    boleto_bancario = pagamentos.filter(tipo=1, forma_pgto=1).aggregate(Sum('valor'))['valor__sum'] or 0
    cartao_credito = pagamentos.filter(tipo=1, forma_pgto=2).aggregate(Sum('valor'))['valor__sum'] or 0
    cartao_debto = pagamentos.filter(tipo=1, forma_pgto=3).aggregate(Sum('valor'))['valor__sum'] or 0
    cheque = pagamentos.filter(tipo=1, forma_pgto=4).aggregate(Sum('valor'))['valor__sum'] or 0
    dinheiro = pagamentos.filter(tipo=1, forma_pgto=5).aggregate(Sum('valor'))['valor__sum'] or 0
    permuta = pagamentos.filter(tipo=1, forma_pgto=6).aggregate(Sum('valor'))['valor__sum'] or 0
    transf_bancaria = pagamentos.filter(tipo=1, forma_pgto=7).aggregate(Sum('valor'))['valor__sum'] or 0
    indefinidos = pagamentos.filter(tipo=1, forma_pgto=None).aggregate(Sum('valor'))['valor__sum'] or 0

    saidas_boleto_bancario = pagamentos.filter(tipo=2, forma_pgto=1).aggregate(Sum('valor'))['valor__sum'] or 0
    saidas_cartao_credito = pagamentos.filter(tipo=2, forma_pgto=2).aggregate(Sum('valor'))['valor__sum'] or 0
    saidas_cartao_debto = pagamentos.filter(tipo=2, forma_pgto=3).aggregate(Sum('valor'))['valor__sum'] or 0
    saidas_cheque = pagamentos.filter(tipo=2, forma_pgto=4).aggregate(Sum('valor'))['valor__sum'] or 0
    saidas_dinheiro = pagamentos.filter(tipo=2, forma_pgto=5).aggregate(Sum('valor'))['valor__sum'] or 0
    saidas_permuta = pagamentos.filter(tipo=2, forma_pgto=6).aggregate(Sum('valor'))['valor__sum'] or 0
    saidas_transf_bancaria = pagamentos.filter(tipo=2, forma_pgto=7).aggregate(Sum('valor'))['valor__sum'] or 0
    saidas_indefinidos = pagamentos.filter(tipo=2, forma_pgto=None).aggregate(Sum('valor'))['valor__sum'] or 0

    ## grafico meios de pgto:
    context['boleto_bancario'] = int(boleto_bancario)
    context['cartao_credito'] = int(cartao_credito)
    context['cartao_debto'] = int(cartao_debto)
    context['cheque'] = int(cheque)
    context['dinheiro'] = int(dinheiro)
    context['permuta'] = int(permuta)
    context['transf_bancaria'] = int(transf_bancaria)
    context['indefinidos'] = int(indefinidos)

    context['saidas_boleto_bancario'] = int(saidas_boleto_bancario)
    context['saidas_cartao_credito'] = int(saidas_cartao_credito)
    context['saidas_cartao_debto'] = int(saidas_cartao_debto)
    context['saidas_cheque'] = int(saidas_cheque)
    context['saidas_dinheiro'] = int(saidas_dinheiro)
    context['saidas_permuta'] = int(saidas_permuta)
    context['saidas_transf_bancaria'] = int(saidas_transf_bancaria)
    context['saidas_indefinidos'] = int(saidas_indefinidos)
    context['entradas'] = entradas
    context['saidas'] = saidas
    context['ano_corrente'] = ANO_CORRENTE
    context['mes_corrente'] = MES_CORRNETE
    
    return render(request, 'index.html', context)


@login_required
def perfis_list(request, escola_pk):
    '''
    Admin: todos
    Diretor: Perfis da escola dele
    Outros: os próprios
    '''
    user = request.user
    escola = get_object_or_404(Escola, pk=escola_pk)
    if not user.can_access_escola(escola.pk):
        raise Http404

    diretor = user.is_diretor(escola_pk)
    admin = user.is_admin()
    form = PerfilSearchForm(request.GET or None, escola=escola)
    context = {}
    
    if admin:
        perfis = form.get_result_queryset()
    elif diretor:
        perfis = form.get_result_queryset().filter(escolas=escola)
    else:
        perfis = form.get_result_queryset().filter(user=user)

    # ### PAGINAÇÃO ####
    get_copy = request.GET.copy()
    context['parameters'] = get_copy.pop('page', True) and get_copy.urlencode()
    page = request.GET.get('page', 1)
    paginator = Paginator(perfis, 15)
    try:
        perfis = paginator.page(page)
    except PageNotAnInteger:
        perfis = paginator.page(1)
    except EmptyPage:
        perfis = paginator.page(paginator.num_pages)
    # ### paginação ####

    context['form'] = form
    context['escola'] = escola
    context['object_list'] = perfis
    context['can_edit'] = diretor or admin
    context['tab_perfis'] = "active"

    return render(request, 'core/perfis_list.html', context)


@login_required
def perfil_form(request, escola_pk, pk=None):
    '''
    Admin: cria, seta senha, vincula a Escola e Group
    Diretor: cria e ou vincula a Escola (dele) e Grupo
    Outros: edita email, nome e troca senha
    '''
    escola = get_object_or_404(Escola, pk=escola_pk)
    if not user.can_access_escola(escola.pk):
        raise Http404
    user = request.user
    if pk:
        perfil = get_object_or_404(Perfil, pk=pk)
        endereco = perfil.endereco_set.last()
        msg = u'Perfil alterado com sucesso.'
    else:
        perfil = None
        endereco = None
        msg = u'Perfil cadastrado.'

    perfil_form = PerfilForm(request.POST or None, instance=perfil, user=user, escola=escola)
    endereco_form = EnderecoForm(request.POST or None, instance=endereco, perfil=perfil, user=user, escola=escola)
    context = {}
    context['perfil_form'] = perfil_form
    context['endereco_form'] = endereco_form
    context['escola'] = escola
    context['tab_aluno'] = "active"

    if request.method == 'POST':
        if perfil_form.is_valid() and endereco_form.is_valid():
            perfil = perfil_form.save()
            # perfil.m2m.save()
            perfil.escolas.add(escola)
            endereco_form.save()
            messages.success(request, msg)
        else:
            msg = 'Falha no cadastro do Perfil: %s - %s' % (perfil_form.errors, endereco_form.errors)
            messages.warning(request, msg)
            return render(request, 'core/perfil_form.html', context)
        return redirect(reverse('perfis_list', kwargs={'escola_pk': escola.pk}))
    return render(request, 'core/perfil_form.html', context)


@login_required
def usuarios_list(request, escola_pk):
    '''
    Admin: todos
    Diretor: Perfis da escola dele
    Outros: os próprios
    '''
    user = request.user
    escola = get_object_or_404(Escola, pk=escola_pk)
    if not user.can_access_escola(escola.pk):
        raise Http404
    diretor = user.is_diretor(escola_pk)
    admin = user.is_admin()

    form = UserSearchForm(request.GET or None, escola=escola)
    usuarios = form.get_result_queryset()
    context = {}

    if diretor:
        usuarios_ids = UserGrupos.objects.filter(escola__pk=escola_pk).values_list('user__id', flat=True)
        usuarios =usuarios.filter(id__in=usuarios_ids)
    else:
        usuarios = usuarios.filter(id=user.id)

    usuarios = usuarios.order_by('nome')

    # ### PAGINAÇÃO ####
    get_copy = request.GET.copy()
    context['parameters'] = get_copy.pop('page', True) and get_copy.urlencode()
    page = request.GET.get('page', 1)
    paginator = Paginator(usuarios, 15)
    try:
        usuarios = paginator.page(page)
    except PageNotAnInteger:
        usuarios = paginator.page(1)
    except EmptyPage:
        usuarios = paginator.page(paginator.num_pages)
    # ### paginação ####
    context['user'] = user
    context['form'] = form
    context['escola'] = escola
    context['object_list'] = usuarios
    context['can_edit'] = admin
    context['tab_usuarios'] = "active"

    return render(request, 'core/usuarios_list.html', context)


@login_required
def usuario_form(request, escola_pk, pk=None):
    '''
    Admin: cria, seta senha, vincula a Escola e Group
    Diretor: cria e ou vincula a Escola (dele) e Grupo
    Outros: edita email, nome e troca senha
    '''
    escola = get_object_or_404(Escola, pk=escola_pk)
    user = request.user
    if pk:
        usuario = get_object_or_404(User, pk=pk)
        msg = u'Usuário alterado com sucesso.'
    else:
        usuario = None
        msg = u'Usuário cadastrado.'

    can_edit = user.is_admin() or user.id == usuario.id
    if not can_edit:
        raise Http404

    form = UserForm(request.POST or None, instance=usuario, user=user, escola=escola)
    context = {}
    context['form'] = form
    context['escola'] = escola
    context['tab_usuarios'] = "active"

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            msg += user.nome
            messages.success(request, msg)
        else:
            messages.warning(request, u'Falha no cadastro do Aluno')
            return render(request, 'core/usuario_form.html', context)
        return redirect(reverse('usuarios_list', kwargs={'escola_pk': escola.pk}))
    return render(request, 'core/usuario_form.html', context)


@login_required
def grupos_list(request, escola_pk=None):
    escola = None
    if escola_pk:
        escola = Escola.objects.get(pk=escola_pk)
    user = request.user
    can_edit = user.is_admin()
    grupos = Group.objects.all()
    if escola:
        grupos = grupos.exclude(name='Admin')
    elif not escola and not can_edit:
        raise Http404
    context = {}
    context['grupos'] = grupos
    context['can_edit'] = can_edit
    context['escola'] = escola
    context['tab_sistema'] = "active"
    context['tab_grupos'] = "active"
    return render(request, 'core/grupos_list.html', context)


@login_required
def grupo_form(request, grupo_pk=None):
    user = request.user
    can_edit = user.is_admin()
    if not can_edit:
        raise Http404
    if grupo_pk:
        grupo = get_object_or_404(Group, pk=grupo_pk)
        msg = u'Grupo alterado com sucesso.'
    else:
        grupo = None
        msg = u'Grupo criado.'

    form = GrupoForm(request.POST or None, instance=grupo)

    if request.method == 'POST':
        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.save()
            messages.success(request, msg)
            return redirect(reverse('grupos_list'))
        else:
            messages.warning(request, u'Falha no cadastro do grupo')

    context = {}
    context['form'] = form

    return render(request, 'core/grupo_form.html', context)
