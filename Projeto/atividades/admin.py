from django.contrib import admin
from .models import RotinaDiaria, RotinaPeriodo, HorarioAtividade


class RotinaPeriodoInline(admin.TabularInline):
    model = RotinaPeriodo
    extra = 0


@admin.register(RotinaDiaria)
class RotinaAdmin(admin.ModelAdmin):
    list_display = ['idoso', 'data']
    list_filter = ['data']
    inlines = [RotinaPeriodoInline]

@admin.register(HorarioAtividade)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'horario', 'dias_semana', 'ativo']
    list_filter = ['tipo', 'ativo']
