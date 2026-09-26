from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Medicamento, PrescricaoMedicamento, RegistroAdministracao
from .forms import MedicamentoForm, PrescricaoForm, AdministracaoForm
from core.decorators import perfil_required, saude_required


@login_required
def lista(request):
    user = request.user
    if user.is_familiar:
        from idosos.models import FamiliarVinculo
        idosos_ids = FamiliarVinculo.objects.filter(familiar=user).values_list('idoso_id', flat=True)
        prescricoes = PrescricaoMedicamento.objects.filter(
            idoso__in=idosos_ids, ativa=True
        ).select_related('idoso', 'medicamento', 'prescrito_por').order_by('idoso__nome')
        return render(request, 'medicamentos/lista.html', {'prescricoes_familiar': prescricoes})
    if not user.pode_ver_saude:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    q = request.GET.get('q', '')
    meds = Medicamento.objects.filter(ativo=True)
    if q:
        meds = meds.filter(Q(nome__icontains=q) | Q(principio_ativo__icontains=q))
    alertas_estoque = Medicamento.objects.filter(estoque_atual__lte=10, ativo=True)
    return render(request, 'medicamentos/lista.html', {'medicamentos': meds, 'q': q, 'alertas': alertas_estoque})


@login_required
def detalhe(request, pk):
    user = request.user
    if user.is_familiar:
        messages.error(request, 'Acesso negado.')
        return redirect('medicamentos:lista')
    if not user.pode_ver_saude:
        messages.error(request, 'Acesso negado.')
        return redirect('dashboard')
    med = get_object_or_404(Medicamento, pk=pk)
    prescricoes = med.prescricoes.select_related('idoso').filter(ativa=True)
    return render(request, 'medicamentos/detalhe.html', {'medicamento': med, 'prescricoes': prescricoes})


@login_required
@perfil_required('administrador', 'enfermeiro')
def novo(request):
    form = MedicamentoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Medicamento cadastrado!')
        return redirect('medicamentos:lista')
    return render(request, 'medicamentos/form.html', {'form': form, 'titulo': 'Novo Medicamento'})


@login_required
@perfil_required('administrador', 'enfermeiro')
def editar(request, pk):
    med = get_object_or_404(Medicamento, pk=pk)
    form = MedicamentoForm(request.POST or None, instance=med)
    if form.is_valid():
        form.save()
        messages.success(request, 'Medicamento atualizado!')
        return redirect('medicamentos:detalhe', pk=pk)
    return render(request, 'medicamentos/form.html', {'form': form, 'titulo': 'Editar Medicamento'})


@login_required
@perfil_required('administrador')
def excluir(request, pk):
    med = get_object_or_404(Medicamento, pk=pk)
    if request.method == 'POST':
        med.ativo = False
        med.save()
        messages.success(request, 'Medicamento desativado.')
        return redirect('medicamentos:lista')
    return render(request, 'medicamentos/confirmar_exclusao.html', {'medicamento': med})


@login_required
@perfil_required('administrador', 'medico')
def nova_prescricao(request, idoso_pk):
    from idosos.models import Idoso
    idoso = get_object_or_404(Idoso, pk=idoso_pk)
    form = PrescricaoForm(request.POST or None)
    if form.is_valid():
        p = form.save(commit=False)
        p.idoso = idoso
        p.prescrito_por = request.user
        p.save()
        messages.success(request, f'Prescrição criada para {idoso.nome}.')
        return redirect('idosos:detalhe', pk=idoso_pk)
    return render(request, 'medicamentos/prescricao_form.html', {'form': form, 'idoso': idoso})


@login_required
@perfil_required('administrador', 'medico', 'enfermeiro')
def registrar_administracao(request, prescricao_pk):
    prescricao = get_object_or_404(PrescricaoMedicamento, pk=prescricao_pk)
    form = AdministracaoForm(request.POST or None)
    if form.is_valid():
        reg = form.save(commit=False)
        reg.prescricao = prescricao
        reg.administrado_por = request.user
        reg.save()
        messages.success(request, 'Administração registrada!')
        return redirect('idosos:detalhe', pk=prescricao.idoso.pk)
    return render(request, 'medicamentos/administracao_form.html', {'form': form, 'prescricao': prescricao})
