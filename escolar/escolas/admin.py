from django.utils.timezone import now
from django.contrib import admin

from escolar.escolas.models import Escola


class EscolaModelAdmin(admin.ModelAdmin):
    list_display = ('nome', 'endereco', 'telefone' , 'created_at', 'escola_criada_hoje')
    date_hierarchy = 'created_at'
    search_fields = ('nome', 'created_at')
    list_filter = ('created_at',)

    def escola_criada_hoje(self, obj):
        return obj.created_at == now().date()

    escola_criada_hoje.short_description = 'criada hoje?'
    escola_criada_hoje.boolean = True

admin.site.register(Escola, EscolaModelAdmin)
