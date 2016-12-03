from django.shortcuts import render

from escolar.escolas.models import Escola

def escolas_list(request):
    escolas = Escola.objects.all()
    return render(request, 'escolas/escolas_list.html', {'escolas': escolas})
