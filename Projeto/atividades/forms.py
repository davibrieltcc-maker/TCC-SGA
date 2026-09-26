from django import forms
from .models import RotinaDiaria, RotinaPeriodo, ChecklistAtividade, ItemChecklist, DIAS_SEMANA_CHOICES


class RotinaDiariaForm(forms.ModelForm):
    class Meta:
        model = RotinaDiaria
        fields = ['idoso', 'data', 'observacoes_gerais']
        widgets = {
            'idoso': forms.Select(attrs={'class': 'form-select', 'id': 'id_idoso'}),
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_data'}),
            'observacoes_gerais': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class RotinaPeriodoForm(forms.ModelForm):
    class Meta:
        model = RotinaPeriodo
        fields = [
            'banho_realizado', 'higiene_oral', 'troca_roupa', 'curativo', 'obs_higiene',
            'refeicoes_realizadas', 'aceitacao_alimentar', 'obs_alimentacao',
        ]
        widgets = {
            'banho_realizado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'higiene_oral': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'troca_roupa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'curativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'obs_higiene': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'refeicoes_realizadas': forms.TextInput(attrs={'class': 'form-control'}),
            'aceitacao_alimentar': forms.Select(attrs={'class': 'form-select'}),
            'obs_alimentacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ChecklistAtividadeForm(forms.ModelForm):
    dias_semana = forms.MultipleChoiceField(
        choices=DIAS_SEMANA_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label='Dias da Semana',
    )

    class Meta:
        model = ChecklistAtividade
        exclude = ['idoso', 'prescrito_por', 'ativo', 'criado_em']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Plano de caminhada'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.dias_semana:
            self.initial['dias_semana'] = self.instance.dias_semana.split(',')

    def clean_dias_semana(self):
        return ','.join(self.cleaned_data['dias_semana'])


ItemChecklistFormSet = forms.inlineformset_factory(
    ChecklistAtividade, ItemChecklist,
    fields=['descricao'], extra=1, can_delete=True,
    widgets={'descricao': forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Ex: Caminhada 20 minutos'
    })},
)
