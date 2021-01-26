import os
from django.db import models


def escola_site_directory_path(instance, documento):
    escola = instance.escola.nome

    path = 'escola_{0}/foto_site/{1}'.format(escola, documento)

    return path

class Conteudo(models.Model):
    '''
    # 10
    Modelo para guardar os dados
    que são conteudo dos sites dos clientes
    - Só admini edita escola e chave
    '''
    escola = models.ForeignKey('escolas.Escola', models.CASCADE)
    chave = models.CharField('Chave', max_length=30)
    titulo = models.CharField('Título', max_length=150, null=True, blank=True)
    texto = models.TextField('Texto', null=True, blank=True)
    foto = models.ImageField('Foto', upload_to=escola_site_directory_path, null=True, blank=True)
    link = models.URLField('link', blank=True, null=True)
    ordem = models.SmallIntegerField('Ordem', null=True, blank=True)

    class Meta:
       ordering = ('ordem',)

    def get_foto_name(self):
        return os.path.basename(self.foto.name)
