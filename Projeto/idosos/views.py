from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Idoso, FamiliarVinculo
from .forms import IdosoForm, FamiliarVinculoForm, CriarFamiliarForm
from core.decorators import perfil_required, admin_ou_recepcionista_required


@login_required
def lista(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', 'ativo')
    idosos = Idoso.objects.all()

    if request.user.is_familiar:
        vinculos = FamiliarVinculo.objects.filter(
            familiar=request.user).values_list('idoso_id', flat=True)
        idosos = idosos.filter(id__in=vinculos)

    if q:
        idosos = idosos.filter(Q(nome__icontains=q) | Q(cpf__icontains=q))
    if status:
        idosos = idosos.filter(status=status)

    return render(request, 'idosos/lista.html', {
        'idosos': idosos, 'q': q, 'status_filtro': status
    })


@login_required
def detalhe(request, pk):
    idoso = get_object_or_404(Idoso, pk=pk)
    if request.user.is_familiar:
        if not FamiliarVinculo.objects.filter(familiar=request.user, idoso=idoso).exists():
            messages.error(request, 'Acesso negado.')
            return redirect('idosos:lista')

    from consultas.models import Consulta, Prontuario
    from medicamentos.models import PrescricaoMedicamento
    from fisioterapia.models import SessaoFisioterapia
    from atividades.models import RotinaDiaria
    from datetime import date

    prontuario = Prontuario.objects.filter(idoso=idoso).first()
    consultas = idoso.consultas.select_related('medico').order_by('-data_hora')[:5]
    prescricoes = idoso.prescricoes.filter(ativa=True).select_related('medicamento', 'prescrito_por')
    sessoes_fisio = idoso.sessoes_fisio.select_related('fisioterapeuta').order_by('-data_hora')[:5]
    rotinas = idoso.rotinas.filter(data=date.today()).prefetch_related('periodos')
    familiares = idoso.familiares.select_related('familiar').all()
    checklists_ativos = idoso.checklists_atividades.filter(ativo=True).prefetch_related('itens')

    return render(request, 'idosos/detalhe.html', {
        'idoso': idoso,
        'prontuario': prontuario,
        'consultas': consultas,
        'prescricoes': prescricoes,
        'sessoes_fisio': sessoes_fisio,
        'rotinas': rotinas,
        'familiares': familiares,
        'checklists_ativos': checklists_ativos,
    })


@login_required
@admin_ou_recepcionista_required
def novo(request):
    form = IdosoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        idoso = form.save()
        messages.success(request, 'Idoso cadastrado! Agora vincule um familiar.')
        return redirect('idosos:vincular_familiar', idoso_pk=idoso.pk)
    return render(request, 'idosos/form.html', {'form': form, 'titulo': 'Novo Idoso'})


@login_required
@admin_ou_recepcionista_required
def editar(request, pk):
    idoso = get_object_or_404(Idoso, pk=pk)
    form = IdosoForm(request.POST or None, request.FILES or None, instance=idoso)
    familiares = idoso.familiares.select_related('familiar').all()
    if form.is_valid():
        form.save()
        messages.success(request, 'Idoso atualizado com sucesso!')
        return redirect('idosos:detalhe', pk=pk)
    return render(request, 'idosos/form.html', {
        'form': form, 'titulo': 'Editar Idoso', 'idoso': idoso, 'familiares': familiares
    })


@login_required
@perfil_required('administrador')
def excluir(request, pk):
    idoso = get_object_or_404(Idoso, pk=pk)
    if request.method == 'POST':
        idoso.delete()
        messages.success(request, 'Idoso removido.')
        return redirect('idosos:lista')
    return render(request, 'idosos/confirmar_exclusao.html', {'idoso': idoso})


@login_required
@admin_ou_recepcionista_required
def vincular_familiar(request, idoso_pk):
    """Vincula ou cria um familiar para um idoso."""
    idoso = get_object_or_404(Idoso, pk=idoso_pk)
    familiares_existentes = idoso.familiares.select_related('familiar').all()

    form_vincular = FamiliarVinculoForm(prefix='vincular', idoso=idoso)
    form_criar = CriarFamiliarForm(prefix='criar')

    if request.method == 'POST':
        acao = request.POST.get('acao')

        if acao == 'vincular':
            form_vincular = FamiliarVinculoForm(request.POST, prefix='vincular', idoso=idoso)
            if form_vincular.is_valid():
                v = form_vincular.save(commit=False)
                v.idoso = idoso
                v.save()
                messages.success(request, 'Familiar vinculado com sucesso!')
                return redirect('idosos:detalhe', pk=idoso_pk)

        elif acao == 'criar':
            form_criar = CriarFamiliarForm(request.POST, prefix='criar')
            if form_criar.is_valid():
                from core.models import Usuario
                familiar = Usuario(
                    username=form_criar.cleaned_data['username'],
                    email=form_criar.cleaned_data['email'],
                    first_name=form_criar.cleaned_data['first_name'],
                    last_name=form_criar.cleaned_data['last_name'],
                    cpf=form_criar.cleaned_data.get('cpf') or None,
                    telefone=form_criar.cleaned_data.get('telefone', ''),
                    perfil='familiar',
                    primeiro_acesso=True,
                    ativo=True,
                )
                familiar.set_unusable_password()
                familiar.save()
                FamiliarVinculo.objects.create(
                    familiar=familiar,
                    idoso=idoso,
                    parentesco=form_criar.cleaned_data['parentesco'],
                    contato_principal=form_criar.cleaned_data.get('contato_principal', False),
                )
                messages.success(
                    request,
                    f'Familiar {familiar.get_full_name()} criado e vinculado! '
                    f'Login: {familiar.username} — ele definirá a senha no primeiro acesso.'
                )
                return redirect('idosos:detalhe', pk=idoso_pk)

        elif acao == 'pular':
            messages.info(request, 'Vínculo familiar não adicionado. Você pode vincular depois na tela do idoso.')
            return redirect('idosos:detalhe', pk=idoso_pk)

    return render(request, 'idosos/vincular_familiar.html', {
        'form_vincular': form_vincular,
        'form_criar': form_criar,
        'idoso': idoso,
        'familiares_existentes': familiares_existentes,
    })


@login_required
@admin_ou_recepcionista_required
def desvincular_familiar(request, idoso_pk, vinculo_pk):
    idoso = get_object_or_404(Idoso, pk=idoso_pk)
    vinculo = get_object_or_404(FamiliarVinculo, pk=vinculo_pk, idoso=idoso)
    if request.method == 'POST':
        vinculo.delete()
        messages.success(request, 'Familiar desvinculado.')
        return redirect('idosos:editar', pk=idoso_pk)
    return render(request, 'idosos/confirmar_exclusao.html', {'vinculo': vinculo, 'idoso': idoso})
