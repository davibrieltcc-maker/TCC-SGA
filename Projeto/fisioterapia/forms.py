from django import forms
from .models import SessaoFisioterapia, PlanoReabilitacao


class SessaoForm(forms.ModelForm):
    class Meta:
        model = SessaoFisioterapia
        # Campos do fluxo de autorizacao ficam fora do form: quem preenche e a
        # view 'autorizar' (medico). Sem isso, o POST do fisioterapeuta zeraria
        # a autorizacao.
        exclude = ['criado_em', 'autorizada', 'autorizado_por', 'data_autorizacao']
        widgets = {
            'idoso': forms.Select(attrs={'class': 'form-select'}),
            'fisioterapeuta': forms.Select(attrs={'class': 'form-select'}),
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'duracao_minutos': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'objetivo': forms.TextInput(attrs={'class': 'form-control'}),
            'procedimentos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'evolucao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # A view 'novo' ja define o fisioterapeuta = usuario logado; nao deve ser
        # obrigatorio no formulario (o campo do model e null=True).
        self.fields['fisioterapeuta'].required = False


class PlanoForm(forms.ModelForm):
    class Meta:
        model = PlanoReabilitacao
        # 'ativo' fora do form: e gerido pelo sistema (default=True). Se ficasse
        # no form sem estar no template, todo POST salvaria ativo=False e o
        # plano sumiria da listagem (que filtra ativo=True).
        exclude = ['criado_em', 'ativo']
        widgets = {
            'idoso': forms.Select(attrs={'class': 'form-select'}),
            'fisioterapeuta': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'objetivo_geral': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'exercicios': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'frequencia_semanal': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_previsao_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fisioterapeuta e preenchido pela view quando quem cria e o proprio
        # fisioterapeuta; para o admin continua sendo uma escolha opcional.
        self.fields['fisioterapeuta'].required = False
