from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from escolar.escolas.models import Escola


@login_required
def escolas_list(request):
    escolas = Escola.objects.all()
    return render(request, 'escolas/escolas_list.html', {'escolas': escolas})
