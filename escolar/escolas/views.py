
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, resolve_url

from escolar.escolas.models import Escola
from escolar.escolas.forms import EscolaForm


@login_required
def escolas_list(request):
    escolas = Escola.objects.all()
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

    return render(
        request,
        'escolas/escola_form.html',
        {
            'form': form,
        }
    )
