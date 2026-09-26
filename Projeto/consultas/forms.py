from django import forms
from .models import Consulta, Prontuario


class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        exclude = ['criado_em', 'atualizado_em']
        widgets = {
            'idoso': forms.Select(attrs={'class': 'form-select'}),
            'medico': forms.Select(attrs={'class': 'form-select'}),
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'queixa_principal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'anamnese': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'exame_fisico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prescricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'retorno_em': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # medico e null=True no model (SET_NULL): pode agendar sem medico
        # definido ainda. So medicos aparecem na lista.
        self.fields['medico'].required = False
        from core.models import Usuario
        self.fields['medico'].queryset = Usuario.objects.filter(perfil='medico', ativo=True)


class ProntuarioForm(forms.ModelForm):
    class Meta:
        model = Prontuario
        exclude = ['idoso', 'criado_em', 'atualizado_em']
        widgets = {
            'historico_familiar': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'historico_pessoal': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cirurgias_anteriores': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vacinas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
