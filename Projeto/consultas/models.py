from django.db import models
from idosos.models import Idoso
from core.models import Usuario


class Consulta(models.Model):
    TIPO_CHOICES = [
        ('rotina', 'Consulta de Rotina'),
        ('urgencia', 'Urgência'),
        ('retorno', 'Retorno'),
        ('especialidade', 'Especialidade'),
        ('preventiva', 'Preventiva'),
    ]
    STATUS_CHOICES = [
        ('agendada', 'Agendada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
        ('falta', 'Falta'),
    ]

    idoso = models.ForeignKey(Idoso, on_delete=models.CASCADE, related_name='consultas')
    medico = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='consultas_medico', limit_choices_to={'perfil': 'medico'})
    data_hora = models.DateTimeField(verbose_name='Data e Hora')
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='rotina')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='agendada')

    # Dados do atendimento
    queixa_principal = models.TextField(blank=True, verbose_name='Queixa Principal')
    anamnese = models.TextField(blank=True, verbose_name='Anamnese')
    exame_fisico = models.TextField(blank=True, verbose_name='Exame Físico')
    diagnostico = models.TextField(blank=True, verbose_name='Diagnóstico')
    prescricao = models.TextField(blank=True, verbose_name='Prescrição / Conduta')
    retorno_em = models.DateField(null=True, blank=True, verbose_name='Retorno Previsto')
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'
        ordering = ['-data_hora']

    def __str__(self):
        return f"{self.idoso.nome} – {self.get_tipo_display()} – {self.data_hora:%d/%m/%Y}"


class Prontuario(models.Model):
    """Prontuário eletrônico do idoso – aglutina histórico de consultas."""
    idoso = models.OneToOneField(Idoso, on_delete=models.CASCADE, related_name='prontuario')
    historico_familiar = models.TextField(blank=True, verbose_name='Histórico Familiar')
    historico_pessoal = models.TextField(blank=True, verbose_name='Histórico Pessoal')
    cirurgias_anteriores = models.TextField(blank=True)
    vacinas = models.TextField(blank=True, verbose_name='Histórico de Vacinas')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Prontuário'
        verbose_name_plural = 'Prontuários'

    def __str__(self):
        return f"Prontuário de {self.idoso.nome}"
