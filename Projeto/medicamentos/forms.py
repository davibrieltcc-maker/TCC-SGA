import re

from django import forms
from .models import Medicamento, PrescricaoMedicamento, RegistroAdministracao

# Frequencias em que faz sentido exigir horario(s) fixo(s).
FREQUENCIAS_COM_HORARIO_FIXO = {
    '1x_dia', '2x_dia', '3x_dia', '4x_dia',
    'cada_6h', 'cada_8h', 'cada_12h', 'semanal',
}


class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        exclude = ['criado_em', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'principio_ativo': forms.TextInput(attrs={'class': 'form-control'}),
            'fabricante': forms.TextInput(attrs={'class': 'form-control'}),
            'forma': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: comprimido, xarope'}),
            'estoque_atual': forms.NumberInput(attrs={'class': 'form-control'}),
            'estoque_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'unidade': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PrescricaoForm(forms.ModelForm):
    class Meta:
        model = PrescricaoMedicamento
        # 'ativa' NAO entra no form: e controlada pelo sistema (default=True na
        # criacao). Se ficasse no form sem estar no template, todo POST salvaria
        # ativa=False e a prescricao sumiria da lista do idoso.
        exclude = ['idoso', 'prescrito_por', 'criado_em', 'ativa']
        widgets = {
            'medicamento': forms.Select(attrs={'class': 'form-select'}),
            'dose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 500mg'}),
            'frequencia': forms.Select(attrs={'class': 'form-select', 'id': 'id_frequencia'}),
            # Preenchido pelos seletores de horario do template (JS). Guardado
            # como texto "HH:MM, HH:MM, ..." para nao mudar o modelo/telas.
            'horarios': forms.HiddenInput(),
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'via_administracao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: oral'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # So permite prescrever medicamentos ativos
        self.fields['medicamento'].queryset = Medicamento.objects.filter(ativo=True).order_by('nome')
        self.fields['horarios'].required = False

    def clean_horarios(self):
        """Normaliza a lista de horarios vinda dos seletores (HH:MM, HH:MM...)."""
        raw = (self.cleaned_data.get('horarios') or '').strip()
        if not raw:
            return ''
        vistos = []
        for parte in raw.split(','):
            p = parte.strip()
            if not p:
                continue
            m = re.match(r'^(\d{1,2}):(\d{2})$', p)
            if not m:
                raise forms.ValidationError(f'Horário inválido: "{p}". Use o formato HH:MM.')
            h, mi = int(m.group(1)), int(m.group(2))
            if h > 23 or mi > 59:
                raise forms.ValidationError(f'Horário inválido: "{p}".')
            valor = f'{h:02d}:{mi:02d}'
            if valor not in vistos:
                vistos.append(valor)
        return ', '.join(sorted(vistos))

    def clean(self):
        cleaned = super().clean()
        if 'horarios' in self.errors:
            return cleaned
        if cleaned.get('frequencia') in FREQUENCIAS_COM_HORARIO_FIXO and not cleaned.get('horarios'):
            self.add_error('horarios', 'Adicione pelo menos um horário para esta frequência.')
        return cleaned


class AdministracaoForm(forms.ModelForm):
    class Meta:
        model = RegistroAdministracao
        exclude = ['prescricao', 'administrado_por', 'criado_em']
        widgets = {
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
