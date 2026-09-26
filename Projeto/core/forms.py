from django import forms
from django.contrib.auth.forms import SetPasswordForm
from .models import Usuario


class UsuarioCreateForm(forms.ModelForm):
    """
    Formulário para criação de usuário pelo Admin ou Recepcionista.
    Não define senha — usuário faz isso no primeiro acesso.
    """
    class Meta:
        model = Usuario
        fields = [
            'first_name', 'last_name', 'username', 'email',
            'perfil', 'cpf', 'telefone', 'foto',
            'data_nascimento', 'especialidade', 'data_admissao',
        ]
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'username': 'Nome de usuário (login)',
            'email': 'E-mail',
        }
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'data_admissao': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # Senha inutilizável — usuário define no primeiro acesso
        user.set_unusable_password()
        user.primeiro_acesso = True
        if commit:
            user.save()
        return user


class UsuarioEditForm(forms.ModelForm):
    """
    Edição de usuário. Recepcionista não pode alterar perfil 'administrador'.
    """
    class Meta:
        model = Usuario
        fields = [
            'first_name', 'last_name', 'email',
            'perfil', 'cpf', 'telefone', 'foto',
            'data_nascimento', 'especialidade', 'data_admissao', 'ativo',
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'data_admissao': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, editor=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Recepcionista não pode mudar perfil do usuário sendo editado
        if editor and editor.is_recepcionista:
            self.fields['perfil'].disabled = True


class DefinirSenhaForm(SetPasswordForm):
    """Formulário para o usuário definir sua senha no primeiro acesso."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = 'Nova senha'
        self.fields['new_password2'].label = 'Confirme a nova senha'
