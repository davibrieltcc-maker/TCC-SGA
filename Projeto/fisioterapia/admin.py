from django.contrib import admin
from .models import SessaoFisioterapia, PlanoReabilitacao

@admin.register(SessaoFisioterapia)
class SessaoAdmin(admin.ModelAdmin):
    list_display = ['idoso', 'fisioterapeuta', 'data_hora', 'status']
    list_filter = ['status']

@admin.register(PlanoReabilitacao)
class PlanoAdmin(admin.ModelAdmin):
    list_display = ['idoso', 'titulo', 'ativo', 'data_inicio']
    list_filter = ['ativo']
