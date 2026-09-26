from django import forms
from .models import Idoso, FamiliarVinculo


class IdosoForm(forms.ModelForm):
    class Meta:
        model = Idoso
        exclude = ['criado_em', 'atualizado_em']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_entrada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'rg': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'tipo_sanguineo': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'numero_quarto': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'alergias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'condicoes_medicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class FamiliarVinculoForm(forms.ModelForm):
    class Meta:
        model = FamiliarVinculo
        fields = ['familiar', 'parentesco', 'contato_principal']
        widgets = {
            'familiar': forms.Select(attrs={'class': 'form-select'}),
            'parentesco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: filho(a), neto(a)'}),
            'contato_principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, idoso=None, **kwargs):
        super().__init__(*args, **kwargs)
        from core.models import Usuario
        if idoso:
            ja_vinculados = FamiliarVinculo.objects.filter(
                idoso=idoso).values_list('familiar_id', flat=True)
            self.fields['familiar'].queryset = Usuario.objects.filter(
                perfil='familiar', ativo=True
            ).exclude(id__in=ja_vinculados)
        else:
            self.fields['familiar'].queryset = Usuario.objects.filter(perfil='familiar', ativo=True)


class CriarFamiliarForm(forms.Form):
    first_name = forms.CharField(
        max_length=150, label='Nome',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=150, label='Sobrenome',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        max_length=150, label='Nome de usuário (login)',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    cpf = forms.CharField(
        max_length=14, required=False, label='CPF',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'})
    )
    telefone = forms.CharField(
        max_length=15, required=False, label='Telefone',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    parentesco = forms.CharField(
        max_length=50, label='Grau de Parentesco',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: filho(a), neto(a)'})
    )
    contato_principal = forms.BooleanField(
        required=False, label='Contato Principal',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        from core.models import Usuario
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nome de usuário já está em uso.')
        return username

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '').strip()
        if cpf:
            from core.models import Usuario
            if Usuario.objects.filter(cpf=cpf).exists():
                raise forms.ValidationError('Este CPF já está cadastrado.')
        return cpf or None
