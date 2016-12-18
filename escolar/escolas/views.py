
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, resolve_url

from escolar.escolas.models import (
    Escola,
    Grupo,
    )
from escolar.escolas.forms import (
    EscolaForm,
    GrupoForm,
    )


@login_required
def escolas_list(request):
    user = request.user
    grupos_ids = user.get_groups_list_ids()
    escolas_pks = Grupo.objects.filter(id__in=grupos_ids).values_list('escola__id', flat=True)
    escolas = Escola.objects.filter(pk__in=escolas_pks)
    return render(request, 'escolas/escolas_list.html', {'escolas': escolas})


@login_required
def escola_form(request, pk=None):
    if pk:
        escola = get_object_or_404(Escola, pk=pk)
        msg = u'Escola alterada com sucesso.'
    else:
        escola = None
        msg = u'Escola criada.'

    form = EscolaForm(request.POST or None, instance=escola)

    if request.method == 'POST':
        if form.is_valid():
            escola = form.save()
            messages.success(request, msg)
            return redirect(reverse('escolas_list'))
        else:
            messages.warning(request, u'Falha no cadastro de escola')

    return render(request,
                        'escolas/escola_form.html', {
                        'form': form})


@login_required
def grupos_list(request):
    user = request.user
    grupos_ids = user.get_groups_list_ids()
    escolas_pks = Grupo.objects.filter(id__in=grupos_ids).values_list('escola__id', flat=True)
    grupos = Grupo.objects.filter(escola__id__in=escolas_pks)
    context = {}
    context['escola'] = Escola.objects.get(id=1)
    context['grupos'] = Grupo.objects.filter(escola__id__in=escolas_pks)
    return render(request, 'escolas/grupos_list.html', context)


@login_required
def grupo_form(request, pk_escola, pk_grupo=None):
    escola = Escola.objects.get(id=pk_escola)
    if pk_grupo:
        grupo = get_object_or_404(Grupo, pk=pk_grupo)
        msg = u'Grupo alterado com sucesso.'
    else:
        grupo = None
        msg = u'Grupo criado.'

    form = GrupoForm(request.POST or None, instance=grupo, escola=escola)

    if request.method == 'POST':
        if form.is_valid():
            grupo = form.save(commit=False)
            grupo.escola = escola
            grupo.save()
            messages.success(request, msg)
            return redirect(reverse('grupos_list'))
        else:
            messages.warning(request, u'Falha no cadastro do grupo')

    context = {}
    context['form'] = form
    context['escola'] = escola

    return render(request, 'escolas/grupo_form.html', context)
