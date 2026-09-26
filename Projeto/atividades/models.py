import re
from datetime import time as time_cls

from django.db import models
from django.db.models import Q

from idosos.models import Idoso
from core.models import Usuario


PERIODO_CHOICES = [
    ('manha', 'Manhã (06h–12h)'),
    ('tarde', 'Tarde (12h–18h)'),
    ('noite', 'Noite (18h–06h)'),
]
PERIODOS_ORDEM = ['manha', 'tarde', 'noite']

REFEICAO_CHOICES = [
    ('cafe', 'Café da manhã'),
    ('lanche_manha', 'Lanche da manhã'),
    ('almoco', 'Almoço'),
    ('lanche_tarde', 'Lanche da tarde'),
    ('jantar', 'Jantar'),
    ('ceia', 'Ceia'),
]


def periodo_do_horario(hora):
    """Classifica um horário (datetime.time) em 'manha', 'tarde' ou 'noite'."""
    if hora is None:
        return None
    h = hora.hour
    if 6 <= h < 12:
        return 'manha'
    if 12 <= h < 18:
        return 'tarde'
    return 'noite'


def _parse_horarios(texto):
    """Extrai horários HH:MM de um texto livre (ex: '08:00, 12:00, 18:00')."""
    horarios = []
    for h_str, m_str in re.findall(r'(\d{1,2}):(\d{2})', texto or ''):
        h, m = int(h_str), int(m_str)
        if 0 <= h < 24 and 0 <= m < 60:
            horarios.append(time_cls(h, m))
    return horarios


class RotinaDiaria(models.Model):
    """Registro do dia inteiro de um idoso, dividido em 3 períodos
    (manhã/tarde/noite) através de RotinaPeriodo."""

    idoso = models.ForeignKey(Idoso, on_delete=models.CASCADE, related_name='rotinas')
    data = models.DateField(verbose_name='Data')
    observacoes_gerais = models.TextField(blank=True, verbose_name='Observações Gerais')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Rotina Diária'
        verbose_name_plural = 'Rotinas Diárias'
        ordering = ['-data']
        unique_together = ('idoso', 'data')

    def __str__(self):
        return f"{self.idoso.nome} – {self.data}"

    def periodos_ordenados(self):
        """Os 3 RotinaPeriodo (existentes ou em branco) na ordem manhã/tarde/noite."""
        existentes = {p.periodo: p for p in self.periodos.all()} if self.pk else {}
        return [
            existentes.get(cod) or RotinaPeriodo(rotina=self, periodo=cod)
            for cod in PERIODOS_ORDEM
        ]


class RotinaPeriodo(models.Model):
    """Checklist de higienização/alimentação de um idoso num período
    (manhã, tarde ou noite) de uma RotinaDiaria."""

    rotina = models.ForeignKey(RotinaDiaria, on_delete=models.CASCADE, related_name='periodos')
    periodo = models.CharField(max_length=6, choices=PERIODO_CHOICES)
    responsavel = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='periodos_registrados')

    # Higienização
    banho_realizado = models.BooleanField(default=False, verbose_name='Banho Realizado')
    higiene_oral = models.BooleanField(default=False, verbose_name='Higiene Oral')
    troca_roupa = models.BooleanField(default=False, verbose_name='Troca de Roupa')
    curativo = models.BooleanField(default=False, verbose_name='Curativo Realizado')
    obs_higiene = models.TextField(blank=True, verbose_name='Obs. Higienização')

    # Alimentação
    refeicoes_realizadas = models.CharField(max_length=200, blank=True, verbose_name='Refeições Realizadas')
    aceitacao_alimentar = models.CharField(
        max_length=10,
        choices=[('total', 'Total'), ('parcial', 'Parcial'), ('recusou', 'Recusou')],
        blank=True,
        verbose_name='Aceitação Alimentar'
    )
    obs_alimentacao = models.TextField(blank=True, verbose_name='Obs. Alimentação')

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Período da Rotina'
        verbose_name_plural = 'Períodos da Rotina'
        ordering = ['rotina', 'periodo']
        unique_together = ('rotina', 'periodo')

    def __str__(self):
        return f"{self.rotina.idoso.nome} – {self.rotina.data} – {self.get_periodo_display()}"


def medicamentos_do_dia(idoso_id, data):
    """Doses de medicamentos programadas para um idoso numa data, separadas
    por período (manhã/tarde/noite) e já anotadas com o registro de
    administração daquele dia (ou None se ainda não registrado)."""
    from medicamentos.models import PrescricaoMedicamento, RegistroAdministracao

    prescricoes = PrescricaoMedicamento.objects.filter(
        idoso_id=idoso_id, ativa=True, data_inicio__lte=data
    ).filter(
        Q(data_fim__isnull=True) | Q(data_fim__gte=data)
    ).select_related('medicamento')

    registros_por_prescricao = {}
    for reg in RegistroAdministracao.objects.filter(
        prescricao__in=prescricoes, data_hora__date=data
    ).order_by('data_hora'):
        registros_por_prescricao.setdefault(reg.prescricao_id, []).append(reg)

    doses = {cod: [] for cod in PERIODOS_ORDEM}
    for p in prescricoes:
        disponiveis = list(registros_por_prescricao.get(p.id, []))
        for horario in sorted(_parse_horarios(p.horarios)):
            periodo = periodo_do_horario(horario)
            registro = None
            for r in disponiveis:
                if periodo_do_horario(r.data_hora.time()) == periodo:
                    registro = r
                    disponiveis.remove(r)
                    break
            doses[periodo].append({
                'prescricao': p, 'horario': horario, 'registro': registro,
            })
    for periodo in doses:
        doses[periodo].sort(key=lambda d: d['horario'])
    return doses


def consultas_do_dia(idoso_id, data):
    """Consultas do idoso numa data, separadas por período."""
    from consultas.models import Consulta

    agrupadas = {cod: [] for cod in PERIODOS_ORDEM}
    consultas = Consulta.objects.filter(
        idoso_id=idoso_id, data_hora__date=data
    ).select_related('medico').order_by('data_hora')
    for c in consultas:
        agrupadas[periodo_do_horario(c.data_hora.time())].append(c)
    return agrupadas


def sessoes_fisio_do_dia(idoso_id, data):
    """Sessões de fisioterapia do idoso numa data, separadas por período."""
    from fisioterapia.models import SessaoFisioterapia

    agrupadas = {cod: [] for cod in PERIODOS_ORDEM}
    sessoes = SessaoFisioterapia.objects.filter(
        idoso_id=idoso_id, data_hora__date=data
    ).select_related('fisioterapeuta').order_by('data_hora')
    for s in sessoes:
        agrupadas[periodo_do_horario(s.data_hora.time())].append(s)
    return agrupadas


class HorarioAtividade(models.Model):
    """Horários fixos de atividades programadas para o asilo."""
    TIPO_CHOICES = [
        ('higiene', 'Higienização'),
        ('alimentacao', 'Alimentação'),
        ('medicamento', 'Medicamento'),
        ('fisioterapia', 'Fisioterapia'),
        ('lazer', 'Atividade de Lazer'),
        ('outro', 'Outro'),
    ]

    titulo = models.CharField(max_length=100)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    horario = models.TimeField(verbose_name='Horário')
    dias_semana = models.CharField(max_length=50, help_text='Ex: seg,ter,qua,qui,sex ou todos')
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Horário de Atividade'
        verbose_name_plural = 'Horários de Atividades'
        ordering = ['horario']

    def __str__(self):
        return f"{self.titulo} – {self.horario:%H:%M}"


DIAS_SEMANA_CHOICES = [
    ('seg', 'Segunda'),
    ('ter', 'Terça'),
    ('qua', 'Quarta'),
    ('qui', 'Quinta'),
    ('sex', 'Sexta'),
    ('sab', 'Sábado'),
    ('dom', 'Domingo'),
]
_CODIGOS_DIAS_SEMANA = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']


class ChecklistAtividade(models.Model):
    """Checklist de atividades personalizadas prescrita para um idoso
    (ex.: caminhada, alongamento), com período e dias da semana em que se aplica."""

    idoso = models.ForeignKey(Idoso, on_delete=models.CASCADE, related_name='checklists_atividades')
    titulo = models.CharField(max_length=150, verbose_name='Título')
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    dias_semana = models.CharField(
        max_length=30, verbose_name='Dias da Semana',
        help_text='Códigos separados por vírgula, ex: seg,qua,sex'
    )
    data_inicio = models.DateField(verbose_name='Início')
    data_fim = models.DateField(null=True, blank=True, verbose_name='Fim (deixe em branco para sem prazo)')
    prescrito_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, related_name='checklists_prescritas')
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Checklist de Atividade'
        verbose_name_plural = 'Checklists de Atividades'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.idoso.nome} – {self.titulo}"

    @property
    def dias_semana_display(self):
        labels = dict(DIAS_SEMANA_CHOICES)
        return ', '.join(labels.get(c, c) for c in self.dias_semana.split(',') if c)

    def aplica_em(self, data):
        """Indica se esta checklist deve ser exibida/registrada na data informada."""
        if not self.ativo or data < self.data_inicio:
            return False
        if self.data_fim and data > self.data_fim:
            return False
        codigo = _CODIGOS_DIAS_SEMANA[data.weekday()]
        return codigo in self.dias_semana.split(',')


class ItemChecklist(models.Model):
    """Uma tarefa dentro de uma checklist de atividades (ex.: 'Caminhada 20 minutos')."""

    checklist = models.ForeignKey(ChecklistAtividade, on_delete=models.CASCADE, related_name='itens')
    descricao = models.CharField(max_length=200, verbose_name='Atividade')
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Item de Checklist'
        verbose_name_plural = 'Itens de Checklist'
        ordering = ['ordem', 'id']

    def __str__(self):
        return self.descricao


class RegistroItemChecklist(models.Model):
    """Execução (ou não) de um item de checklist em um dia específico."""

    item = models.ForeignKey(ItemChecklist, on_delete=models.CASCADE, related_name='registros')
    data = models.DateField()
    realizado = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Registro de Item de Checklist'
        verbose_name_plural = 'Registros de Itens de Checklist'
        ordering = ['-data']
        unique_together = ('item', 'data')

    def __str__(self):
        status = '✓' if self.realizado else '—'
        return f"{status} {self.item.descricao} – {self.data}"


def itens_checklist_do_dia(idoso_id, data):
    """Itens de checklist aplicáveis a um idoso numa data, cada um já anotado
    com `.registro_do_dia` (o RegistroItemChecklist daquele dia, ou None se
    ainda não foi registrado). Não altera nada — apenas consulta.
    """
    checklists = ChecklistAtividade.objects.filter(
        idoso_id=idoso_id, ativo=True).prefetch_related('itens')
    itens = [item for c in checklists if c.aplica_em(data) for item in c.itens.all()]
    registros = {
        r.item_id: r
        for r in RegistroItemChecklist.objects.filter(item__in=itens, data=data)
    }
    for item in itens:
        item.registro_do_dia = registros.get(item.id)
    return itens
