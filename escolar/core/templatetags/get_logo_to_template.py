# coding: utf-8
from django import template
from escolar.escolas.models import Escola

register = template.Library()

'''
ref #86
'''

@register.filter
def get_logo(slug):

    if slug:
        escola = Escola.objects.get(slug=slug)
        if escola.logo:
            return escola.logo
    return None
