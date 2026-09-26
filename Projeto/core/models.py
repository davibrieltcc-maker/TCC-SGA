from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    PERFIL_CHOICES = [
        ('administrador', 'Administrador'),
        ('medico', 'Médico'),
        ('fisioterapeuta', 'Fisioterapeuta'),
        ('enfermeiro', 'Enfermeiro(a)'),
        ('recepcionista', 'Recepcionista'),
        ('familiar', 'Familiar do Idoso'),
    ]

    perfil = models.CharField(
        max_length=20, choices=PERFIL_CHOICES,
        default='recepcionista', verbose_name='Perfil de Acesso'
    )
    telefone = models.CharField(max_length=15, blank=True, verbose_name='Telefone')
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True, verbose_name='CPF')
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True, verbose_name='Foto')
    data_nascimento = models.DateField(null=True, blank=True, verbose_name='Data de Nascimento')
    especialidade = models.CharField(
        max_length=100, blank=True, verbose_name='Especialidade',
        help_text='Preencha para Médico ou Fisioterapeuta'
    )
    data_admissao = models.DateField(null=True, blank=True, verbose_name='Data de Admissão')
    primeiro_acesso = models.BooleanField(
        default=True, verbose_name='Primeiro Acesso',
        help_text='Usuário deve definir senha no primeiro login'
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_perfil_display()})"

    # ── Verificações de perfil ──────────────────────────────────────────
    @property
    def is_administrador(self):
        return self.perfil == 'administrador' or self.is_superuser

    @property
    def is_medico(self):
        return self.perfil == 'medico'

    @property
    def is_fisioterapeuta(self):
        return self.perfil == 'fisioterapeuta'

    @property
    def is_enfermeiro(self):
        return self.perfil == 'enfermeiro'

    @property
    def is_recepcionista(self):
        return self.perfil == 'recepcionista'

    @property
    def is_familiar(self):
        return self.perfil == 'familiar'

    # ── Permissões compostas ────────────────────────────────────────────
    @property
    def pode_editar_saude(self):
        """Apenas médico e admin podem editar prontuário."""
        return self.is_administrador or self.is_medico

    @property
    def pode_ver_saude(self):
        """Profissionais de saúde + admin visualizam módulos clínicos."""
        return (self.is_administrador or self.is_medico
                or self.is_fisioterapeuta or self.is_enfermeiro)

    @property
    def pode_cadastrar_usuarios(self):
        """Admin e recepcionista criam/editam usuários."""
        return self.is_administrador or self.is_recepcionista

    @property
    def pode_cadastrar_idosos(self):
        """Admin e recepcionista cadastram idosos."""
        return self.is_administrador or self.is_recepcionista

    @property
    def pode_administrar(self):
        return self.is_administrador
