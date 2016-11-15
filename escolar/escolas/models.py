from django.db import models
from municipios.models import Municipio


class Escola(models.Model):
    nome=models.CharField(max_length=200)
    endereco=models.CharField(max_length=200)
    numero=models.CharField(max_length=10)
    telefone = models.CharField(max_length=14, null=True, blank=True)
    complemento = models.CharField(max_length=100, null=True, blank=True)
    bairro = models.CharField(max_length=100)
    municipio = models.ForeignKey(Municipio)


