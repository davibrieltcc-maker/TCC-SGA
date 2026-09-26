from django.contrib import admin
from .models import Consulta, Prontuario

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ['idoso', 'medico', 'data_hora', 'tipo', 'status']
    list_filter = ['status', 'tipo']

@admin.register(Prontuario)
class ProntuarioAdmin(admin.ModelAdmin):
    list_display = ['idoso', 'criado_em', 'atualizado_em']
