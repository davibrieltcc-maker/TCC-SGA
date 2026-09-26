from django.db import models
from idosos.models import Idoso
from core.models import Usuario


class Medicamento(models.Model):
    """Cadastro geral de medicamentos disponíveis no asilo."""
    nome = models.CharField(max_length=150, verbose_name='Nome do Medicamento')
    principio_ativo = models.CharField(max_length=150, blank=True)
    fabricante = models.CharField(max_length=100, blank=True)
    forma = models.CharField(max_length=50, blank=True, verbose_name='Forma Farmacêutica', help_text='Ex: comprimido, xarope, injeção')
    estoque_atual = models.IntegerField(default=0, verbose_name='Estoque Atual')
    estoque_minimo = models.IntegerField(default=10, verbose_name='Estoque Mínimo')
    unidade = models.CharField(max_length=20, default='unidade', verbose_name='Unidade de Medida')
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Medicamento'
        verbose_name_plural = 'Medicamentos'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def estoque_baixo(self):
        return self.estoque_atual <= self.estoque_minimo


class PrescricaoMedicamento(models.Model):
    """Prescrição de medicamento para um idoso específico."""
    FREQUENCIA_CHOICES = [
        ('1x_dia', '1x ao dia'),
        ('2x_dia', '2x ao dia'),
        ('3x_dia', '3x ao dia'),
        ('4x_dia', '4x ao dia'),
        ('cada_6h', 'A cada 6 horas'),
        ('cada_8h', 'A cada 8 horas'),
        ('cada_12h', 'A cada 12 horas'),
        ('sob_demanda', 'Sob demanda'),
        ('semanal', 'Semanal'),
        ('customizado', 'Customizado'),
    ]

    idoso = models.ForeignKey(Idoso, on_delete=models.CASCADE, related_name='prescricoes')
    medicamento = models.ForeignKey(Medicamento, on_delete=models.PROTECT, related_name='prescricoes')
    prescrito_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='prescricoes_feitas', limit_choices_to={'perfil': 'medico'})
    dose = models.CharField(max_length=50, verbose_name='Dose')
    frequencia = models.CharField(max_length=15, choices=FREQUENCIA_CHOICES)
    horarios = models.CharField(max_length=200, blank=True, verbose_name='Horários', help_text='Ex: 08:00, 12:00, 18:00')
    data_inicio = models.DateField(verbose_name='Início')
    data_fim = models.DateField(null=True, blank=True, verbose_name='Fim (deixe em branco para uso contínuo)')
    via_administracao = models.CharField(max_length=50, blank=True, verbose_name='Via de Administração', help_text='Ex: oral, subcutânea, intravenosa')
    observacoes = models.TextField(blank=True)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Prescrição'
        verbose_name_plural = 'Prescrições'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.idoso.nome} – {self.medicamento.nome} ({self.dose})"


class RegistroAdministracao(models.Model):
    """Registro de cada vez que um medicamento foi administrado a um idoso."""
    STATUS_CHOICES = [
        ('administrado', 'Administrado'),
        ('recusado', 'Recusado pelo idoso'),
        ('adiado', 'Adiado'),
        ('omitido', 'Omitido'),
    ]

    prescricao = models.ForeignKey(PrescricaoMedicamento, on_delete=models.CASCADE, related_name='registros')
    administrado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='administracoes')
    data_hora = models.DateTimeField(verbose_name='Data e Hora')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='administrado')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de Administração'
        verbose_name_plural = 'Registros de Administração'
        ordering = ['-data_hora']

    def __str__(self):
        return f"{self.prescricao.idoso.nome} – {self.prescricao.medicamento.nome} – {self.data_hora:%d/%m/%Y %H:%M}"
