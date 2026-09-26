from django.db import models
from core.models import Usuario


class Idoso(models.Model):
    SEXO_CHOICES = [('M', 'Masculino'), ('F', 'Feminino')]
    TIPO_SANGUINEO = [('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-')]
    STATUS_CHOICES = [('ativo','Ativo'),('inativo','Inativo'),('internado','Internado'),('falecido','Falecido')]

    nome = models.CharField(max_length=150, verbose_name='Nome Completo')
    data_nascimento = models.DateField(verbose_name='Data de Nascimento')
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    rg = models.CharField(max_length=20, blank=True)
    tipo_sanguineo = models.CharField(max_length=3, choices=TIPO_SANGUINEO, blank=True)
    foto = models.ImageField(upload_to='idosos/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ativo')

    # Endereço
    endereco = models.CharField(max_length=200, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    cep = models.CharField(max_length=9, blank=True)

    # Dados médicos
    alergias = models.TextField(blank=True, verbose_name='Alergias')
    condicoes_medicas = models.TextField(blank=True, verbose_name='Condições Médicas')
    observacoes = models.TextField(blank=True, verbose_name='Observações Gerais')

    # Controle
    data_entrada = models.DateField(verbose_name='Data de Entrada')
    numero_quarto = models.CharField(max_length=10, blank=True, verbose_name='Quarto')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Idoso'
        verbose_name_plural = 'Idosos'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def idade(self):
        from datetime import date
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )


class FamiliarVinculo(models.Model):
    """Vincula um usuário familiar a um ou mais idosos."""
    familiar = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='idosos_vinculados', limit_choices_to={'perfil': 'familiar'})
    idoso = models.ForeignKey(Idoso, on_delete=models.CASCADE, related_name='familiares')
    parentesco = models.CharField(max_length=50, verbose_name='Parentesco')
    contato_principal = models.BooleanField(default=False, verbose_name='Contato Principal')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Vínculo Familiar'
        verbose_name_plural = 'Vínculos Familiares'
        unique_together = ('familiar', 'idoso')

    def __str__(self):
        return f"{self.familiar.get_full_name()} → {self.idoso.nome} ({self.parentesco})"
