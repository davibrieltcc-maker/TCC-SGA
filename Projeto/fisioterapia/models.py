from django.db import models
from idosos.models import Idoso
from core.models import Usuario


class SessaoFisioterapia(models.Model):
    STATUS_CHOICES = [
        ('agendada', 'Agendada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
        ('falta', 'Falta do Idoso'),
    ]

    idoso = models.ForeignKey(
        Idoso, on_delete=models.CASCADE, related_name='sessoes_fisio')
    fisioterapeuta = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True,
        related_name='sessoes_realizadas',
        limit_choices_to={'perfil': 'fisioterapeuta'})
    data_hora = models.DateTimeField(verbose_name='Data e Hora')
    duracao_minutos = models.IntegerField(default=45, verbose_name='Duração (min)')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='agendada')
    objetivo = models.CharField(max_length=200, blank=True, verbose_name='Objetivo da Sessão')
    procedimentos = models.TextField(blank=True, verbose_name='Procedimentos Realizados')
    evolucao = models.TextField(blank=True, verbose_name='Evolução do Paciente')
    observacoes = models.TextField(blank=True)

    # ── Fluxo de autorização médica (RN006) ────────────────────────────
    autorizada = models.BooleanField(
        default=False, verbose_name='Autorizada pelo Médico',
        help_text='Sessão só pode ser executada após autorização médica.')
    autorizado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='sessoes_autorizadas',
        limit_choices_to={'perfil': 'medico'},
        verbose_name='Autorizado por')
    data_autorizacao = models.DateTimeField(
        null=True, blank=True, verbose_name='Data da Autorização')

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Sessão de Fisioterapia'
        verbose_name_plural = 'Sessões de Fisioterapia'
        ordering = ['-data_hora']

    def __str__(self):
        status_auth = '✓' if self.autorizada else '⏳'
        return f"{status_auth} {self.idoso.nome} – {self.data_hora:%d/%m/%Y %H:%M}"


class PlanoReabilitacao(models.Model):
    idoso = models.ForeignKey(
        Idoso, on_delete=models.CASCADE, related_name='planos_reab')
    fisioterapeuta = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True,
        limit_choices_to={'perfil': 'fisioterapeuta'})
    titulo = models.CharField(max_length=150, verbose_name='Título do Plano')
    objetivo_geral = models.TextField(verbose_name='Objetivo Geral')
    exercicios = models.TextField(verbose_name='Exercícios Prescritos')
    frequencia_semanal = models.IntegerField(default=3, verbose_name='Sessões por Semana')
    data_inicio = models.DateField()
    data_previsao_fim = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Plano de Reabilitação'
        verbose_name_plural = 'Planos de Reabilitação'

    def __str__(self):
        return f"{self.idoso.nome} – {self.titulo}"
