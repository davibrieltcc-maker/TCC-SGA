from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Consulta, Prontuario
from .forms import ConsultaForm, ProntuarioForm
from core.decorators import perfil_required, saude_required


@login_required
def lista(request):
    user = request.user
    if user.is_familiar:
        from idosos.models import FamiliarVinculo
        idosos_ids = FamiliarVinculo.objects.filter(familiar=user).values_list('idoso_id', flat=True)
        consultas = Consulta.objects.filter(
            idoso__in=idosos_ids
        ).select_related('idoso', 'medico').order_by('-data_hora')
        return render(request, 'consultas/lista.html', {'consultas': consultas})
    if not user.pode_ver_saude:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    consultas = Consulta.objects.select_related('idoso', 'medico').order_by('-data_hora')[:50]
    return render(request, 'consultas/lista.html', {'consultas': consultas})


@login_required
def detalhe(request, pk):
    user = request.user
    consulta = get_object_or_404(Consulta, pk=pk)
    if user.is_familiar:
        from idosos.models import FamiliarVinculo
        if not FamiliarVinculo.objects.filter(familiar=user, idoso=consulta.idoso).exists():
            messages.error(request, 'Acesso negado.')
            return redirect('consultas:lista')
        return render(request, 'consultas/detalhe.html', {'consulta': consulta})
    if not user.pode_ver_saude:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    return render(request, 'consultas/detalhe.html', {'consulta': consulta})

@login_required
@perfil_required('administrador', 'medico', 'recepcionista')
def novo(request):
    form = ConsultaForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Consulta agendada!')
        return redirect('consultas:lista')
    return render(request, 'consultas/form.html', {'form': form, 'titulo': 'Nova Consulta'})

@login_required
@perfil_required('administrador', 'medico')
def editar(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)
    form = ConsultaForm(request.POST or None, instance=consulta)
    if form.is_valid():
        form.save()
        messages.success(request, 'Consulta atualizada!')
        return redirect('consultas:lista')
    return render(request, 'consultas/form.html', {'form': form, 'titulo': 'Editar Consulta'})

@login_required
@perfil_required('administrador')
def excluir(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)
    if request.method == 'POST':
        consulta.delete()
        return redirect('consultas:lista')
    return render(request, 'consultas/confirmar_exclusao.html', {'consulta': consulta})


# ── Prontuário ────────────────────────────────────────────────────────────────

@login_required
def prontuario(request, idoso_pk):
    from idosos.models import Idoso, FamiliarVinculo
    idoso = get_object_or_404(Idoso, pk=idoso_pk)
    user = request.user

    if user.is_familiar:
        if not FamiliarVinculo.objects.filter(familiar=user, idoso=idoso).exists():
            messages.error(request, 'Acesso negado.')
            return redirect('idosos:lista')
        prontuario_obj, _ = Prontuario.objects.get_or_create(idoso=idoso)
        consultas = idoso.consultas.select_related('medico').order_by('-data_hora')[:10]
        return render(request, 'consultas/prontuario.html', {
            'idoso': idoso, 'prontuario': prontuario_obj, 'consultas': consultas, 'somente_leitura': True
        })

    if not user.pode_ver_saude:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')

    prontuario_obj, _ = Prontuario.objects.get_or_create(idoso=idoso)
    pode_editar = user.is_administrador or user.is_medico or user.is_enfermeiro

    if request.method == 'POST' and pode_editar:
        form = ProntuarioForm(request.POST, instance=prontuario_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prontuário atualizado!')
            return redirect('consultas:prontuario', idoso_pk=idoso_pk)
    else:
        form = ProntuarioForm(instance=prontuario_obj)

    consultas = idoso.consultas.select_related('medico').order_by('-data_hora')
    return render(request, 'consultas/prontuario.html', {
        'idoso': idoso, 'prontuario': prontuario_obj, 'form': form,
        'consultas': consultas, 'somente_leitura': not pode_editar
    })
