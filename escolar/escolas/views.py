# coding: utf-8
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from escolar.core.models import UserGrupos, User
from django.contrib.auth.models import Group

from escolar.core.forms import (
    EnderecoForm,
)

from escolar.escolas.models import (
    Aluno,
    Autorizado,
    AutorizadoAluno,
    Escola,
    Classe,
    ClasseAluno,
    MembroFamilia,
)
from escolar.escolas.forms import (
    AlunoForm,
    AlunoSearchForm,
    AutorizadoForm,
    ClasseForm,
    ClasseAlunoForm,
    ClasseProfessorForm,
    EscolaForm,
    MembroFamiliaForm,
    ProfessorForm,
)

from escolar.financeiro.models import ContratoAluno
from escolar.financeiro.forms import ano_corrente, ContratoAlunoSearchForm

@login_required
def autorizado_form(request, aluno_pk, autorizado_pk=None):
    user = request.user  # TODO: deve ser os Pais OU Diretor
    aluno = Aluno.objects.get(id=aluno_pk)
    escola = aluno.escola
    
    can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
    if not can_edit:
        raise Http404

    classe = None  # aluno.get_classe(escola)
    autorizado = None
    msg = u'Autorizado cadastrado.'

    if autorizado_pk:
        autorizado = get_object_or_404(Autorizado, pk=autorizado_pk)
        msg = u'Autorizado alterado com sucesso.'
    form = AutorizadoForm(request.POST or None,
                          instance=autorizado,
                          escola=escola,
                          aluno=aluno,
                          responsavel=user)

    if request.method == 'POST':
        if form.is_valid():
            autorizado = form.save()
            messages.success(request, msg)
            return redirect(reverse('autorizado_cadastro', kwargs={'aluno_pk': aluno.pk, 'autorizado_pk': autorizado.id}))
        else:
            messages.warning(request, u'Falha no cadastro do Autorizado')

    context = {}
    context['can_edit'] = can_edit
    context['form'] = form
    context['escola'] = escola
    context['aluno'] = aluno
    context['classe'] = classe
    context['autorizado'] = autorizado
    context['tab_alunos'] = "active"
    context['tab_autorizados_aluno'] = "active"

    return render(request, 'escolas/autorizado_form.html', context)


@login_required
def autorizado_cadastro(request, aluno_pk, autorizado_pk):
    user = request.user  # TODO: deve ser os Pais OU Diretor
    aluno = Aluno.objects.get(id=aluno_pk)
    escola = aluno.escola
    
    can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
    if not can_edit:
        raise Http404

    classe = None  # aluno.get_classe(escola)

    autorizado = get_object_or_404(Autorizado, pk=autorizado_pk)

    context = {}
    context['can_edit'] = can_edit
    context['escola'] = escola
    context['aluno'] = aluno
    context['classe'] = classe
    context['autorizado'] = autorizado
    context['tab_alunos'] = "active"
    context['tab_autorizados_aluno'] = "active"

    return render(request, 'escolas/autorizado_cadastro.html', context)

@login_required
def autorizados_list(request, escola_pk):
    '''
    ref #22
    Todos Autorizados de  
    todos Alunos
    '''
    user = request.user
    escola = get_object_or_404(Escola, pk=escola_pk)
    autorizados = AutorizadoAluno.objects.filter(escola_id=escola_pk)
    can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
    context = {}
    context['escola'] = escola
    context['autorizados'] = autorizados
    context['tab_autorizados'] = "active"
    context['can_edit'] = can_edit

    return render(request, 'escolas/autorizados_alunos_list.html', context)


@login_required
def autorizados_aluno_list(request, aluno_pk):
    '''
    ref #22
    Todos Autorizados de Um Aluno
    '''
    user = request.user
    aluno = get_object_or_404(Aluno, pk=aluno_pk)
    escola = aluno.escola
    autorizados = AutorizadoAluno.objects.filter(aluno=aluno)
    # autorizados = Autorizado.objects.filter(id__in=autorizados_ids)

    can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
    context = {}
    context['escola'] = escola
    context['aluno'] = aluno
    context['can_edit'] = can_edit
    context['autorizados'] = autorizados
    context['tab_alunos'] = "active"
    context['tab_autorizados_aluno'] = "active"

    return render(request, 'escolas/autorizados_do_aluno_list.html', context)

@login_required
def escolas_list(request):
    user = request.user
    escolas_ids = user.usergrupos_set.all().values_list('escola__id', flat=True)
    if user.is_admin():
        escolas = Escola.objects.all()
    else:
        escolas =  Escola.objects.filter(id__in=escolas_ids)
    context = {}
    context['can_create'] = user.is_admin()
    context['escolas'] = escolas
    context['tab_escola'] = "active"
    return render(request, 'escolas/escolas_list.html', context)


@login_required
def escola_form(request, pk=None):
    user = request.user
    admin = can_edit = user.is_admin()
    if pk:
        escola = get_object_or_404(Escola, pk=pk)
        msg = u'Escola alterada com sucesso.'
        can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
        if not can_edit:
            raise Http404
    else:
        escola = None
        msg = u'Escola criada.' 

    form = EscolaForm(request.POST or None, request.FILES or None, instance=escola, user=user)
    context = {}
    context['form'] = form
    context['escola'] = escola
    context['admin'] = admin
    context['tab_escola'] = "active"

    if request.method == 'POST':
        if form.is_valid():
            escola = form.save()
            messages.success(request, msg)
            return redirect(reverse('escola_cadastro', kwargs={'pk': escola.pk}))
        else:
            messages.warning(request, u'Falha no cadastro de escola')

    return render(request, 'escolas/escola_form.html', context)


@login_required
def escola_cadastro(request, pk):
    user = request.user
    escola = get_object_or_404(Escola, pk=pk)
    if not user.can_access_escola(pk):
        raise Http404
    can_edit = any([user.is_admin(), user.is_diretor(escola.id)])
    context = {}
    context["escola"] = escola
    context['tab_escola'] = "active"
    context['can_edit'] = can_edit
    return render(request, 'escolas/escola_cadastro.html', context)


@login_required
def professores_list(request, escola_pk):
    user = request.user
    escola = Escola.objects.get(id=escola_pk)
    professores_ids = UserGrupos.objects.filter(grupo__name='Professor',escola__pk=escola_pk).values_list('user__id', flat=True)
    professores = User.objects.filter(id__in=professores_ids)
    for professor in professores:
        professor.classes = professor.get_professor_classes(escola)
        professor.status = professor.usergrupos_set.filter(grupo__name='Professor', escola=escola).last().ativo
    context = {}
    context['escola'] = escola
    context['professores'] = professores
    context['escola'] = escola
    context['can_edit'] = any([user.is_admin(), user.is_diretor(escola_pk)])
    context['user'] = user
    context['tab_professores'] = "active"
    return render(request, 'escolas/professores_list.html', context)


@login_required
def professor_form(request, escola_pk, professor_pk=None):
    '''
    professor é user
    Não cria aqui, já foi definido no cadastro do user
    '''
    escola = Escola.objects.get(id=escola_pk)
    grupo = Group.objects.filter(name='Professor')
    professor = None
    if professor_pk:
        professor = User.objects.get(pk=professor_pk)

    if professor_pk:
        grupo_user = get_object_or_404(UserGrupos, escola=escola_pk, user=professor_pk, grupo=grupo)
        msg = u'Professor alterado com sucesso.'
    else:
        grupo_user = None
        msg = u'Professor cadastrado.'

    form = ProfessorForm(request.POST or None, instance=grupo_user)

    if request.method == 'POST':
        if form.is_valid():
            grupo_user = form.save()
            messages.success(request, msg)
            return redirect(reverse('professores_list', kwargs={'escola_pk': escola.pk}))
        else:
            messages.warning(request, u'Falha no cadastro do Professor')

    context = {}
    context['form'] = form
    context['escola'] = escola
    context['grupo_user'] = grupo_user
    context['tab_professores'] = "active"
    context['professor'] = professor

    return render(request, 'escolas/professor_form.html', context)


@login_required
def alunos_list(request, escola_pk):
    user = request.user
    if not user.can_access_escola(escola_pk):
        raise Http404
    can_edit = any([user.is_admin(), user.is_diretor(escola_pk)])
    escola = get_object_or_404(Escola, pk=escola_pk)
    context = {}
    
    form = AlunoSearchForm(request.GET or None, escola=escola)
    if form.is_valid():
        alunos = form.get_result_queryset()
    else:
        alunos = form.get_result_queryset().filter(ano=ano_corrente)

    # ### PAGINAÇÃO ####
    get_copy = request.GET.copy()
    context['parameters'] = get_copy.pop('page', True) and get_copy.urlencode()
    page = request.GET.get('page', 1)
    paginator = Paginator(alunos, 15)
    try:
        alunos = paginator.page(page)
    except PageNotAnInteger:
        alunos = paginator.page(1)
    except EmptyPage:
        alunos = paginator.page(paginator.num_pages)
    # ### paginação ####

    context['form'] = form
    context['escola'] = escola 
    context['can_edit'] = can_edit
    context['object_list'] = alunos
    context['user'] = user
    context['tab_alunos'] = "active"

    return render(request, 'escolas/alunos_list.html', context)

@login_required
def aluno_form(request, escola_pk, aluno_pk=None):
    '''
    aluno é Aluno, e pode ou não ter um User
    '''
    user = request.user
    escola = Escola.objects.get(id=escola_pk)
    can_edit = any([user.is_admin(), user.is_diretor(escola_pk)])

    if aluno_pk:
        aluno = get_object_or_404(Aluno, escola=escola_pk, pk=aluno_pk)
        endereco = aluno.endereco
        msg = u'Aluno alterado com sucesso.'
    else:
        aluno = None
        endereco = None
        msg = u'Aluno cadastrado.'

    form = AlunoForm(request.POST or None, request.FILES or None, instance=aluno, user=user, escola=escola)
    endereco_form = EnderecoForm(request.POST or None, instance=endereco, user=user, escola=escola)

    if request.method == 'POST':
        if form.is_valid() and endereco_form.is_valid():
            endereco = endereco_form.save()
            aluno = form.save()
            aluno.endereco = endereco
            aluno.save()
            messages.success(request, msg)
            return redirect(reverse('aluno_cadastro', kwargs={'aluno_pk': aluno.pk}))
        else:
            messages.warning(request, u'Falha no cadastro do Aluno')

    context = {}
    context['form'] = form
    context['escola'] = escola
    context['aluno'] = aluno
    context['can_edit'] = can_edit
    context['endereco_form'] = endereco_form
    context['tab_alunos'] = "active"
    context['tab_aluno'] = "active"

    # context['classes'] = aluno.get_all_classe(escola)

    return render(request, 'escolas/aluno_form.html', context)

@login_required
def aluno_cadastro(request, aluno_pk):
    '''

    '''
    user = request.user
    aluno = get_object_or_404(Aluno, pk=aluno_pk)
    escola = aluno.escola
    if not user.can_access_escola(escola.pk):
        raise Http404
    can_edit = any([user.is_admin(), user.is_diretor(escola.pk)])

    context = {}
    context['escola'] = escola
    context['aluno'] = aluno
    context['can_edit'] = can_edit

    context['tab_alunos'] = "active"
    context['tab_aluno'] = "active"

    # context['classes'] = aluno.get_all_classe(escola)

    return render(request, 'escolas/aluno_cadastro.html', context)


@login_required
def membro_familia_form(request,  aluno_pk, membro_pk=None):
    '''
    #33
    são os responsáveis pelo aluno, se Menor de Idade
    resp financeiro e ou pedagógico
    '''
    user = request.user
    aluno = get_object_or_404(Aluno, pk=aluno_pk)
    escola = get_object_or_404(Escola, id=aluno.escola.pk)
    can_edit = any([user.is_admin(), user.is_diretor(escola.pk)])
    if not can_edit:
        raise Http404
    
    if membro_pk:
        membro = get_object_or_404(MembroFamilia, pk=membro_pk)
        msg = u'Membro da família alterado com sucesso.'
    else:
        membro = None
        msg = u'Membro da família.'

    form = MembroFamiliaForm(request.POST or None, request.FILES or None, instance=membro, user=user, aluno=aluno)

    if request.method == 'POST':
        if form.is_valid():
            memnbro = form.save()
            messages.success(request, msg)
            return redirect(reverse('membro_familia_cadastro', kwargs={'aluno_pk': aluno.pk, 'membro_pk': membro.id}))
        else:
            messages.warning(request, u'Falha no cadastro do membro família')

    context = {}
    context['form'] = form
    context['membro'] = membro
    context['aluno'] = aluno
    context['escola'] = escola
    context['tab_alunos'] = "active"
    context['tab_responsaveis_aluno'] = "active"

    return render(request, 'escolas/membro_familia_form.html', context)

@login_required
def membro_familia_cadastro(request,  aluno_pk, membro_pk):
    '''
    #33
    são os responsáveis pelo aluno, se Menor de Idade
    resp financeiro e ou pedagógico
    '''
    user = request.user
    aluno = get_object_or_404(Aluno, pk=aluno_pk)
    escola = get_object_or_404(Escola, id=aluno.escola.pk)
    can_edit = any([user.is_admin(), user.is_diretor(escola.pk)])
    if not user.can_access_escola(escola.pk):
        raise Http404
    
    membro = get_object_or_404(MembroFamilia, pk=membro_pk)

    
    context = {}
    context['membro'] = membro
    context['aluno'] = aluno
    context['escola'] = escola
    context['can_edit'] = can_edit
    context['tab_alunos'] = "active"
    context['tab_responsaveis_aluno'] = "active"

    return render(request, 'escolas/membro_familia_cadastro.html', context)

@login_required
def membros_familia_list(request, aluno_pk):
    user = request.user
    aluno = get_object_or_404(Aluno, pk=aluno_pk)
    escola = get_object_or_404(Escola, pk=aluno.escola.pk)
    can_edit = any([user.is_admin(), user.is_diretor(escola.pk)])

    context = {}
    context['escola'] = escola 
    context['can_edit'] = can_edit
    context['object_list'] = MembroFamilia.objects.filter(aluno=aluno)
    context['user'] = user
    context['aluno'] = aluno
    context['tab_alunos'] = "active"
    context['tab_responsaveis_aluno'] = "active"

    return render(request, 'escolas/membros_familia_aluno_list.html', context)


@login_required
def classe_form(request, escola_pk, classe_pk=None):
    '''
    Classes "isolarão":
    escola;
    curso, ex: 5º ano ensino fundamental A, 5º ano B, ...
    ano: 2017, 2018, ...
    período: manhã, tarde, noite
    >>
    professores que dão aula para determinada classe
    alunos que pertencem a uma classe

    user não pode trocar o ID da escola
    '''
    escola = Escola.objects.get(id=escola_pk)

    if not request.user.is_diretor(escola.id):
        raise Http404

    classe = None
    msg = u'Classe cadastrada.'

    if classe_pk:
        classe = get_object_or_404(Classe, pk=classe_pk)
        msg = u'Classe alterada com sucesso.'

    form = ClasseForm(request.POST or None, instance=classe, escola=escola)

    if request.method == 'POST':
        if form.is_valid():
            classe = form.save()
            messages.success(request, msg)
            return redirect(reverse('classes_list', kwargs={'escola_pk': escola.pk}))
        else:
            messages.warning(request, u'Falha no cadastro do Classe')

    context = {}
    context['form'] = form
    context['escola'] = escola
    context['classe'] = classe
    context['tab_classes'] = "active"

    return render(request, 'escolas/classe_form.html', context)


@login_required
def classes_list(request, escola_pk):
    user = request.user
    escola = Escola.objects.get(id=escola_pk)
    can_edit = any([user.is_admin(), user.is_diretor(escola_pk)])
    if user.get_professor_classes(escola):
        classes = user.get_professor_classes(escola)
    else:
        classes = Classe.objects.filter(escola__pk=escola_pk)
    print(classes.count())
    context = {}
    context['classes'] = classes
    context['escola'] = escola
    context['can_edit'] = can_edit
    context['user'] = user
    context['tab_classes'] = "active"

    return render(request, 'escolas/classes_list.html', context)



@login_required
def classe_aluno_form(request, classe_pk, classe_aluno_pk=None):
    classe = get_object_or_404(Classe, pk=classe_pk)
    classe_aluno = None
    msg = 'Vinculação classe aluno criada'

    escola = Escola.objects.get(id=classe.escola.id)
    if not request.user.is_diretor(escola.id):
        raise Http404

    if classe_aluno_pk:
        classe_aluno = get_object_or_404(ClasseAluno, pk=classe_aluno_pk)
        msg = 'Vinculação classe aluno editada'

    form = ClasseAlunoForm(request.POST or None, instance=classe_aluno, classe=classe)

    if request.method == 'POST':
        if form.is_valid():
            classe_aluno = form.save()
            messages.success(request, msg)
            return redirect(reverse('classes_list', kwargs={'escola_pk': escola.pk}))
        else:
            messages.warning(request, u'Falha no cadastro do Aluno')

    context = {}
    context['form'] = form
    context['escola'] = escola
    context['classe_aluno'] = classe_aluno
    context['tab_classes'] = "active"
    context['classe'] = classe

    return render(request, 'escolas/classe_aluno_form.html', context)


@login_required
def classe_professor_form(request, classe_pk, classe_professor_pk=None):
    classe = get_object_or_404(Classe, pk=classe_pk)
    classe_professor = None
    msg = 'Vinculação classe professor criada'

    escola = Escola.objects.get(id=classe.escola.id)

    if not request.user.is_diretor(escola.id):
        raise Http404

    if classe_professor_pk:
        classe_professor = get_object_or_404(ClasseAluno, pk=classe_professor_pk)
        msg = 'Vinculação classe professor editada'

    form = ClasseProfessorForm(request.POST or None, instance=classe_professor, classe=classe)

    if request.method == 'POST':
        if form.is_valid():
            classe_professor = form.save()
            messages.success(request, msg)
            return redirect(reverse('classes_list', kwargs={'escola_pk': escola.pk}))
        else:
            messages.warning(request, u'Falha no cadastro do Professor')

    context = {}
    context['form'] = form
    context['escola'] = escola
    context['classe_professor'] = classe_professor
    context['tab_classes'] = "active"
    context['classe'] = classe

    return render(request, 'escolas/classe_professor_form.html', context)
