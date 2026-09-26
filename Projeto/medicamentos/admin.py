from django.contrib import admin
from .models import Medicamento, PrescricaoMedicamento, RegistroAdministracao

@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'principio_ativo', 'estoque_atual', 'estoque_minimo', 'ativo']
    list_filter = ['ativo']

@admin.register(PrescricaoMedicamento)
class PrescricaoAdmin(admin.ModelAdmin):
    list_display = ['idoso', 'medicamento', 'dose', 'frequencia', 'ativa']
    list_filter = ['ativa', 'frequencia']

@admin.register(RegistroAdministracao)
class RegistroAdmin(admin.ModelAdmin):
    list_display = ['prescricao', 'administrado_por', 'data_hora', 'status']
    list_filter = ['status']
