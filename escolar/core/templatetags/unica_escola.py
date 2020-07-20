# coding: utf-8
from django import template
from escolar.escolas.models import Escola
from escolar.financeiro.models import BandeiraEscolaParametro

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

@register.filter
def is_diretor(user, escola):
    return user.is_diretor(escola.id)

@register.filter
def is_professor(user, escola):
    return user.is_professor(escola.id)

@register.filter
def is_aluno(user, escola):
    return user.is_aluno(escola.id)

@register.filter
def get_logo(slug):
    """
    TODO
    se tem a escola mas não tem o logo
    entrega o nome
    se não tem a escola
    entrega uma imagme padrão, um logo do sistema
    """

    if slug:
        escola = Escola.objects.filter(slug=slug).first()
        if escola and escola.logo:
            return escola.logo.url
    return None

@register.filter
def get_bandeira_parametros(bandeira, escola):
    return BandeiraEscolaParametro.objects.filter(escola=escola, bandeira=bandeira).first()
