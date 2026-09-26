from django.db import models
from core.models import Usuario


class Funcionario(models.Model):
    """Perfil profissional dos funcionários do asilo."""
    VINCULO_CHOICES = [
        ('clt', 'CLT'),
        ('pj', 'Pessoa Jurídica'),
        ('voluntario', 'Voluntário'),
        ('estagio', 'Estágio'),
    ]

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='funcionario')
    registro_profissional = models.CharField(max_length=30, blank=True, verbose_name='Registro Profissional (CRM/CREFITO etc.)')
    especialidade = models.CharField(max_length=100, blank=True)
    vinculo = models.CharField(max_length=12, choices=VINCULO_CHOICES, default='clt')
    data_admissao = models.DateField(verbose_name='Data de Admissão')
    data_demissao = models.DateField(null=True, blank=True, verbose_name='Data de Demissão')
    salario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    carga_horaria = models.IntegerField(default=44, verbose_name='Carga Horária Semanal (h)')
    turno = models.CharField(max_length=20, blank=True, verbose_name='Turno de Trabalho')
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'

    def __str__(self):
        return self.usuario.get_full_name()

    @property
    def ativo(self):
        return self.data_demissao is None
