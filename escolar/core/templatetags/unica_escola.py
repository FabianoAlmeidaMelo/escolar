# coding: utf-8
from django import template
from escolar.escolas.models import Escola

register = template.Library()

'''
ref #27
'''

@register.filter
def get_escola(user):
    escola_id = user.get_unica_escola()

    if escola_id:
        return Escola.objects.get(id=escola_id)
    return None


@register.filter
def get_grupos_escola(user, escola):
    return user.usergrupos_set.filter(escola=escola).exclude(grupo__name='Admin')