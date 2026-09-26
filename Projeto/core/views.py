from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import date, timedelta

from .models import Usuario
from .forms import UsuarioCreateForm, UsuarioEditForm, DefinirSenhaForm
from .decorators import admin_ou_recepcionista_required, admin_required


# ── Autenticação ─────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Primeiro acesso: usuário criado sem senha — não precisa de senha para entrar
        try:
            candidate = Usuario.objects.get(username=username, ativo=True)
            if candidate.primeiro_acesso and not candidate.has_usable_password():
                candidate.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, candidate)
                return redirect('definir_senha')
        except Usuario.DoesNotExist:
            pass

        # Autenticação normal
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.ativo:
                messages.error(request, 'Usuário inativo. Contate o administrador.')
            else:
                login(request, user)
                if user.primeiro_acesso:
                    return redirect('definir_senha')
                return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def definir_senha(request):
    """Fluxo de primeiro acesso: usuário define sua própria senha."""
    form = DefinirSenhaForm(user=request.user, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        request.user.primeiro_acesso = False
        request.user.save(update_fields=['primeiro_acesso'])
        messages.success(request, 'Senha definida com sucesso! Bem-vindo ao sistema.')
        return redirect('dashboard')
    return render(request, 'auth/definir_senha.html', {'form': form})


# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    # Bloqueia usuário de primeiro acesso
    if request.user.primeiro_acesso:
        return redirect('definir_senha')

    from idosos.models import Idoso
    from medicamentos.models import Medicamento
    from consultas.models import Consulta
    from fisioterapia.models import SessaoFisioterapia
    from atividades.models import RotinaDiaria

    hoje = date.today()
    ctx = {'hoje': hoje}

    if request.user.pode_cadastrar_idosos:
        ctx['total_idosos'] = Idoso.objects.filter(status='ativo').count()
        ctx['total_funcionarios'] = Usuario.objects.filter(ativo=True).exclude(perfil='familiar').count()

    if request.user.pode_ver_saude:
        ctx['consultas_hoje'] = Consulta.objects.filter(
            data_hora__date=hoje, status='agendada').count()
        ctx['sessoes_fisio_hoje'] = SessaoFisioterapia.objects.filter(
            data_hora__date=hoje, status='agendada',
            autorizada=True).count()
        from django.db.models import F
        ctx['medicamentos_estoque_baixo'] = Medicamento.objects.filter(
            estoque_atual__lte=F('estoque_minimo'), ativo=True).count()
        ctx['consultas_proximas'] = Consulta.objects.filter(
            data_hora__date__range=[hoje, hoje + timedelta(days=7)],
            status='agendada'
        ).select_related('idoso', 'medico').order_by('data_hora')[:5]
        ctx['sessoes_pendentes_autorizacao'] = SessaoFisioterapia.objects.filter(
            autorizada=False, status='agendada').count()

    if request.user.is_familiar:
        from idosos.models import FamiliarVinculo
        vinculos = FamiliarVinculo.objects.filter(
            familiar=request.user).select_related('idoso')
        idosos_ids = vinculos.values_list('idoso_id', flat=True)
        ctx['idosos_familiar'] = Idoso.objects.filter(id__in=idosos_ids)
        ctx['rotinas_hoje'] = RotinaDiaria.objects.filter(
            idoso__in=idosos_ids, data=hoje
        ).select_related('idoso').prefetch_related('periodos')

    return render(request, 'dashboard/dashboard.html', ctx)


# ── Gestão de Usuários ────────────────────────────────────────────────────────

@login_required
@admin_ou_recepcionista_required
def usuarios_lista(request):
    """Admin e Recepcionista listam usuários (exceto outros admins para recepcionista)."""
    usuarios = Usuario.objects.all().order_by('perfil', 'first_name')
    if request.user.is_recepcionista:
        # Recepcionista não vê outros administradores
        usuarios = usuarios.exclude(perfil='administrador')
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})


@login_required
@admin_ou_recepcionista_required
def usuario_novo(request):
    """Cria novo usuário. Sem senha inicial — usuário define no 1º acesso."""
    form = UsuarioCreateForm(request.POST or None, request.FILES or None)

    # Recepcionista não pode criar Administrador
    if request.user.is_recepcionista:
        form.fields['perfil'].choices = [
            c for c in Usuario.PERFIL_CHOICES if c[0] != 'administrador'
        ]

    if form.is_valid():
        form.save()
        messages.success(request, 'Usuário criado! O usuário deve definir sua senha no primeiro acesso.')
        return redirect('usuarios_lista')
    return render(request, 'usuarios/form.html', {'form': form, 'titulo': 'Novo Usuário'})


@login_required
@admin_ou_recepcionista_required
def usuario_editar(request, pk):
    """Edita usuário. Recepcionista não pode editar Admin."""
    usuario = get_object_or_404(Usuario, pk=pk)

    # Recepcionista não pode editar administrador
    if request.user.is_recepcionista and usuario.is_administrador:
        messages.error(request, 'Recepcionista não pode editar o perfil Administrador.')
        return redirect('usuarios_lista')

    form = UsuarioEditForm(
        request.POST or None,
        request.FILES or None,
        instance=usuario,
        editor=request.user
    )
    if form.is_valid():
        form.save()
        messages.success(request, 'Usuário atualizado!')
        return redirect('usuarios_lista')
    return render(request, 'usuarios/form.html', {'form': form, 'titulo': 'Editar Usuário', 'usuario': usuario})


@login_required
@admin_required
def usuario_excluir(request, pk):
    """Apenas admin pode desativar usuários."""
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.ativo = False
        usuario.save(update_fields=['ativo'])
        messages.success(request, f'Usuário {usuario.get_full_name()} desativado.')
        return redirect('usuarios_lista')
    return render(request, 'usuarios/confirmar_exclusao.html', {'usuario': usuario})
