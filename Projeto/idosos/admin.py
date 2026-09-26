from django.contrib import admin
from .models import Idoso, FamiliarVinculo

@admin.register(Idoso)
class IdosoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'data_nascimento', 'numero_quarto', 'status']
    list_filter = ['status', 'sexo']
    search_fields = ['nome', 'cpf']

@admin.register(FamiliarVinculo)
class FamiliarVinculoAdmin(admin.ModelAdmin):
    list_display = ['familiar', 'idoso', 'parentesco', 'contato_principal']
