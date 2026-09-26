from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import SessaoFisioterapia, PlanoReabilitacao
from .forms import SessaoForm, PlanoForm
from core.decorators import perfil_required, saude_required, familiar_bloqueado


@login_required
def lista(request):
    user = request.user
    if user.is_familiar:
        from idosos.models import FamiliarVinculo
        ids = FamiliarVinculo.objects.filter(familiar=user).values_list('idoso_id', flat=True)
        sessoes = SessaoFisioterapia.objects.filter(
            idoso__in=ids).select_related('idoso', 'fisioterapeuta').order_by('-data_hora')
        return render(request, 'fisioterapia/lista.html', {'sessoes': sessoes, 'pendentes_autorizacao': 0})
    if not user.pode_ver_saude:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')

    sessoes = SessaoFisioterapia.objects.select_related(
        'idoso', 'fisioterapeuta', 'autorizado_por'
    ).order_by('-data_hora')[:50]

    pendentes = SessaoFisioterapia.objects.filter(
        autorizada=False, status='agendada').count() if user.is_medico or user.is_administrador else 0

    return render(request, 'fisioterapia/lista.html', {
        'sessoes': sessoes,
        'pendentes_autorizacao': pendentes,
    })


@login_required
def detalhe(request, pk):
    sessao = get_object_or_404(SessaoFisioterapia, pk=pk)
    # Familiar só pode ver seu idoso
    if request.user.is_familiar:
        from idosos.models import FamiliarVinculo
        if not FamiliarVinculo.objects.filter(
                familiar=request.user, idoso=sessao.idoso).exists():
            messages.error(request, 'Acesso negado.')
            return redirect('fisioterapia:lista')
    return render(request, 'fisioterapia/detalhe.html', {'sessao': sessao})


@login_required
@perfil_required('fisioterapeuta')
def novo(request):
    """Fisioterapeuta cria sessão — fica pendente de autorização médica."""
    form = SessaoForm(request.POST or None)
    if form.is_valid():
        sessao = form.save(commit=False)
        sessao.fisioterapeuta = request.user
        sessao.autorizada = False  # sempre inicia sem autorização
        sessao.save()
        messages.success(
            request,
            'Sessão agendada! Aguardando autorização do médico responsável.'
        )
        return redirect('fisioterapia:lista')
    return render(request, 'fisioterapia/form.html', {
        'form': form, 'titulo': 'Nova Sessão de Fisioterapia'
    })


@login_required
@perfil_required('medico')
def autorizar(request, pk):
    """Médico autoriza a execução de uma sessão de fisioterapia (RN006)."""
    sessao = get_object_or_404(SessaoFisioterapia, pk=pk, autorizada=False)
    if request.method == 'POST':
        sessao.autorizada = True
        sessao.autorizado_por = request.user
        sessao.data_autorizacao = timezone.now()
        sessao.save(update_fields=['autorizada', 'autorizado_por', 'data_autorizacao'])
        messages.success(
            request,
            f'Sessão de {sessao.idoso.nome} autorizada com sucesso!'
        )
        return redirect('fisioterapia:lista')
    return render(request, 'fisioterapia/autorizar.html', {'sessao': sessao})


@login_required
@perfil_required('medico')
def rejeitar(request, pk):
    """Médico rejeita/cancela uma sessão pendente."""
    sessao = get_object_or_404(SessaoFisioterapia, pk=pk, autorizada=False)
    if request.method == 'POST':
        sessao.status = 'cancelada'
        sessao.observacoes += f'\n[Rejeitada por {request.user.get_full_name()} em {timezone.now():%d/%m/%Y %H:%M}]'
        sessao.save(update_fields=['status', 'observacoes'])
        messages.warning(request, 'Sessão rejeitada.')
        return redirect('fisioterapia:lista')
    return render(request, 'fisioterapia/rejeitar.html', {'sessao': sessao})


@login_required
@perfil_required('fisioterapeuta')
def editar(request, pk):
    """Fisioterapeuta edita sessão não autorizada ainda."""
    sessao = get_object_or_404(SessaoFisioterapia, pk=pk)
    if sessao.autorizada:
        messages.error(request, 'Não é possível editar uma sessão já autorizada.')
        return redirect('fisioterapia:detalhe', pk=pk)
    form = SessaoForm(request.POST or None, instance=sessao)
    if form.is_valid():
        form.save()
        messages.success(request, 'Sessão atualizada!')
        return redirect('fisioterapia:lista')
    return render(request, 'fisioterapia/form.html', {
        'form': form, 'titulo': 'Editar Sessão'
    })


@login_required
@perfil_required('fisioterapeuta')
def registrar_evolucao(request, pk):
    """Fisioterapeuta registra evolução após executar a sessão autorizada."""
    sessao = get_object_or_404(SessaoFisioterapia, pk=pk, autorizada=True)
    if request.method == 'POST':
        sessao.evolucao = request.POST.get('evolucao', '')
        sessao.procedimentos = request.POST.get('procedimentos', '')
        sessao.status = 'realizada'
        sessao.save(update_fields=['evolucao', 'procedimentos', 'status'])
        messages.success(request, 'Evolução registrada!')
        return redirect('fisioterapia:detalhe', pk=pk)
    return render(request, 'fisioterapia/evolucao_form.html', {'sessao': sessao})


@login_required
@perfil_required('administrador')
def excluir(request, pk):
    sessao = get_object_or_404(SessaoFisioterapia, pk=pk)
    if request.method == 'POST':
        sessao.delete()
        return redirect('fisioterapia:lista')
    return render(request, 'fisioterapia/confirmar_exclusao.html', {'sessao': sessao})


# ── Plano de Reabilitação ─────────────────────────────────────────────────────

@login_required
def planos_lista(request):
    user = request.user
    if user.is_familiar:
        from idosos.models import FamiliarVinculo
        ids = FamiliarVinculo.objects.filter(familiar=user).values_list('idoso_id', flat=True)
        planos = PlanoReabilitacao.objects.filter(idoso__in=ids, ativo=True).select_related('idoso', 'fisioterapeuta')
        return render(request, 'fisioterapia/planos_lista.html', {'planos': planos})
    if not user.pode_ver_saude:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    planos = PlanoReabilitacao.objects.select_related('idoso', 'fisioterapeuta').filter(ativo=True)
    return render(request, 'fisioterapia/planos_lista.html', {'planos': planos})


@login_required
@perfil_required('fisioterapeuta', 'administrador')
def plano_novo(request):
    form = PlanoForm(request.POST or None)
    if form.is_valid():
        plano = form.save(commit=False)
        if request.user.is_fisioterapeuta:
            plano.fisioterapeuta = request.user
        plano.save()
        messages.success(request, 'Plano de reabilitação criado!')
        return redirect('fisioterapia:planos_lista')
    return render(request, 'fisioterapia/plano_form.html', {'form': form, 'titulo': 'Novo Plano de Reabilitação'})


@login_required
@perfil_required('fisioterapeuta', 'administrador')
def plano_editar(request, pk):
    plano = get_object_or_404(PlanoReabilitacao, pk=pk)
    form = PlanoForm(request.POST or None, instance=plano)
    if form.is_valid():
        form.save()
        messages.success(request, 'Plano atualizado!')
        return redirect('fisioterapia:planos_lista')
    return render(request, 'fisioterapia/plano_form.html', {'form': form, 'titulo': 'Editar Plano', 'plano': plano})


@login_required
@perfil_required('administrador')
def plano_excluir(request, pk):
    plano = get_object_or_404(PlanoReabilitacao, pk=pk)
    if request.method == 'POST':
        plano.ativo = False
        plano.save(update_fields=['ativo'])
        messages.success(request, 'Plano encerrado.')
        return redirect('fisioterapia:planos_lista')
    return render(request, 'fisioterapia/confirmar_exclusao.html', {'plano': plano})
