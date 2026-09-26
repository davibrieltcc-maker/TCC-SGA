from django import forms
from django.db.models import Q
from .models import Funcionario


class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        exclude = ['criado_em']
        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'registro_profissional': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidade': forms.TextInput(attrs={'class': 'form-control'}),
            'vinculo': forms.Select(attrs={'class': 'form-select'}),
            'data_admissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_demissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'salario': forms.NumberInput(attrs={'class': 'form-control'}),
            'carga_horaria': forms.NumberInput(attrs={'class': 'form-control'}),
            'turno': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Evita escolher um usuario que ja tem ficha de funcionario (OneToOne).
        from core.models import Usuario
        qs = Usuario.objects.filter(ativo=True).exclude(perfil='familiar')
        if self.instance and self.instance.pk:
            qs = qs.filter(Q(funcionario__isnull=True) | Q(pk=self.instance.usuario_id))
        else:
            qs = qs.filter(funcionario__isnull=True)
        self.fields['usuario'].queryset = qs.order_by('first_name', 'last_name')
