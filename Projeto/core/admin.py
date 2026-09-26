from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'perfil', 'ativo', 'email']
    list_filter = ['perfil', 'ativo']
    fieldsets = UserAdmin.fieldsets + (
        ('Perfil do Sistema', {'fields': ('perfil', 'telefone', 'cpf', 'foto', 'ativo')}),
    )
