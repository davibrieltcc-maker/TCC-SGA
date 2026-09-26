from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import date, datetime
from .models import (
    RotinaDiaria, RotinaPeriodo, HorarioAtividade, ChecklistAtividade, ItemChecklist,
    RegistroItemChecklist, itens_checklist_do_dia, medicamentos_do_dia,
    consultas_do_dia, sessoes_fisio_do_dia, PERIODOS_ORDEM, PERIODO_CHOICES,
)
from .forms import RotinaDiariaForm, RotinaPeriodoForm, ChecklistAtividadeForm, ItemChecklistFormSet
from core.decorators import perfil_required


ORDENACOES = {
    'recentes': ('-data', 'idoso__nome'),
    'antigas': ('data', 'idoso__nome'),
    'nome_asc': ('idoso__nome', '-data'),
    'nome_desc': ('-idoso__nome', '-data'),
}


def _anexar_resumo_checklist(rotinas):
    """Anota cada rotina com `.checklist_resumo`: os itens de checklist do
    idoso aplicáveis naquele dia, com o status de execução (ou pendente)."""
    rotinas = list(rotinas)
    cache = {}
    for r in rotinas:
        chave = (r.idoso_id, r.data)
        if chave not in cache:
            cache[chave] = itens_checklist_do_dia(r.idoso_id, r.data)
        r.checklist_resumo = cache[chave]
    return rotinas


@login_required
def lista(request):
    user = request.user
    data_param = request.GET.get('data', '').strip()
    idoso_param = request.GET.get('idoso', '').strip()
    ordenar_param = request.GET.get('ordenar', 'recentes').strip()
    if ordenar_param not in ORDENACOES:
        ordenar_param = 'recentes'

    # Valida a data se foi informada
    data_valida = None
    if data_param:
        try:
            datetime.strptime(data_param, '%Y-%m-%d')
            data_valida = data_param
        except ValueError:
            data_valida = None

    if user.is_familiar:
        from idosos.models import FamiliarVinculo, Idoso
        idosos_ids = list(FamiliarVinculo.objects.filter(
            familiar=user).values_list('idoso_id', flat=True))
        rotinas = RotinaDiaria.objects.filter(idoso__in=idosos_ids)
        idosos_filtro = Idoso.objects.filter(id__in=idosos_ids).order_by('nome')
        horarios = []
    else:
        rotinas = RotinaDiaria.objects.all()
        from idosos.models import Idoso
        idosos_filtro = Idoso.objects.order_by('nome')
        horarios = HorarioAtividade.objects.filter(ativo=True).order_by('horario')

    rotinas = rotinas.prefetch_related('periodos')
    if data_valida:
        rotinas = rotinas.filter(data=data_valida)
    if idoso_param.isdigit():
        rotinas = rotinas.filter(idoso_id=idoso_param)
    rotinas = rotinas.order_by(*ORDENACOES[ordenar_param])

    return render(request, 'atividades/lista.html', {
        'rotinas': _anexar_resumo_checklist(rotinas),
        'data_filtro': data_valida or '',
        'idoso_filtro': idoso_param,
        'ordenar_filtro': ordenar_param,
        'idosos_filtro': idosos_filtro,
        'horarios': horarios,
    })


@login_required
def detalhe(request, pk):
    rotina = get_object_or_404(RotinaDiaria, pk=pk)
    checklist_itens = itens_checklist_do_dia(rotina.idoso_id, rotina.data)
    return render(request, 'atividades/detalhe.html', {
        'rotina': rotina,
        'periodos': rotina.periodos_ordenados(),
        'periodo_labels': dict(PERIODO_CHOICES),
        'medicamentos': medicamentos_do_dia(rotina.idoso_id, rotina.data),
        'consultas': consultas_do_dia(rotina.idoso_id, rotina.data),
        'fisioterapias': sessoes_fisio_do_dia(rotina.idoso_id, rotina.data),
        'checklist_itens': checklist_itens,
    })


def _salvar_registros_checklist(request, rotina):
    """Grava/atualiza a execução dos itens de checklist marcados na tela de Rotina.

    Os ids dos itens exibidos vêm num campo oculto ('checklist_item_ids'),
    já que checkboxes desmarcados simplesmente não aparecem no POST.
    """
    ids = [i for i in request.POST.get('checklist_item_ids', '').split(',') if i]
    for id_str in ids:
        item = ItemChecklist.objects.filter(pk=id_str, checklist__idoso=rotina.idoso).first()
        if not item:
            continue
        RegistroItemChecklist.objects.update_or_create(
            item=item, data=rotina.data,
            defaults={
                'realizado': request.POST.get(f'item_realizado_{id_str}') == 'on',
                'observacoes': request.POST.get(f'item_obs_{id_str}', '').strip(),
                'registrado_por': request.user,
            }
        )


def _salvar_medicamentos(request, rotina):
    """Grava/atualiza os registros de administração de medicamento marcados
    no checklist da Rotina (checkbox 'tomado' + horário administrado)."""
    from medicamentos.models import PrescricaoMedicamento, RegistroAdministracao

    chaves = [c for c in request.POST.get('med_slot_keys', '').split(',') if c]
    for chave in chaves:
        partes = chave.split(':')
        if len(partes) != 3:
            continue
        prescricao_id, _periodo, _hhmm = partes
        prescricao = PrescricaoMedicamento.objects.filter(
            pk=prescricao_id, idoso=rotina.idoso).first()
        if not prescricao:
            continue

        tomado = request.POST.get(f'med_tomado_{chave}') == 'on'
        horario_str = request.POST.get(f'med_horario_{chave}', '').strip()
        registro_id = request.POST.get(f'med_registro_{chave}', '').strip()

        if not tomado and not registro_id:
            continue  # não marcado e sem registro anterior: nada a fazer

        try:
            h, m = (int(x) for x in horario_str.split(':')[:2])
        except ValueError:
            agora = datetime.now()
            h, m = agora.hour, agora.minute
        data_hora = datetime.combine(rotina.data, datetime.min.time()).replace(hour=h, minute=m)

        defaults = {
            'prescricao': prescricao,
            'administrado_por': request.user,
            'data_hora': data_hora,
            'status': 'administrado' if tomado else 'omitido',
        }
        if registro_id:
            RegistroAdministracao.objects.filter(pk=registro_id).update(**defaults)
        else:
            RegistroAdministracao.objects.create(**defaults)


def _salvar_consultas(request, rotina):
    """Marca consultas do dia como 'realizada' (ou volta para 'agendada')
    conforme o checkbox do checklist. Não altera consultas já canceladas
    ou com falta registrada."""
    from consultas.models import Consulta

    ids = [i for i in request.POST.get('consulta_ids', '').split(',') if i]
    for cid in ids:
        consulta = Consulta.objects.filter(pk=cid, idoso=rotina.idoso).first()
        if not consulta or consulta.status not in ('agendada', 'realizada'):
            continue
        realizada = request.POST.get(f'consulta_realizada_{cid}') == 'on'
        novo_status = 'realizada' if realizada else 'agendada'
        if consulta.status != novo_status:
            consulta.status = novo_status
            consulta.save(update_fields=['status'])


def _salvar_fisioterapias(request, rotina):
    """Marca sessões de fisioterapia do dia como 'realizada' (ou volta para
    'agendada') conforme o checkbox do checklist."""
    from fisioterapia.models import SessaoFisioterapia

    ids = [i for i in request.POST.get('fisio_ids', '').split(',') if i]
    for sid in ids:
        sessao = SessaoFisioterapia.objects.filter(pk=sid, idoso=rotina.idoso).first()
        if not sessao or sessao.status not in ('agendada', 'realizada'):
            continue
        realizada = request.POST.get(f'fisio_realizada_{sid}') == 'on'
        novo_status = 'realizada' if realizada else 'agendada'
        if sessao.status != novo_status:
            sessao.status = novo_status
            sessao.save(update_fields=['status'])


def _preparar_periodos(rotina):
    """Dict periodo -> RotinaPeriodo (existente ou novo, ainda não salvo)."""
    existentes = {p.periodo: p for p in rotina.periodos.all()} if rotina.pk else {}
    return {
        cod: existentes.get(cod) or RotinaPeriodo(periodo=cod)
        for cod in PERIODOS_ORDEM
    }


def _salvar_periodos(rotina, periodo_forms, request):
    for cod, pform in periodo_forms.items():
        periodo = pform.save(commit=False)
        periodo.rotina = rotina
        periodo.periodo = cod
        if not periodo.responsavel_id:
            periodo.responsavel = request.user
        periodo.save()


def _processar_checklist_dia(request, rotina):
    _salvar_registros_checklist(request, rotina)
    _salvar_medicamentos(request, rotina)
    _salvar_consultas(request, rotina)
    _salvar_fisioterapias(request, rotina)


@login_required
@perfil_required('administrador', 'enfermeiro', 'recepcionista')
def novo(request):
    idoso_inicial = request.GET.get('idoso')
    form = RotinaDiariaForm(request.POST or None, initial={
        'data': date.today(),
        'idoso': idoso_inicial,
    })
    periodo_forms = {
        cod: RotinaPeriodoForm(request.POST or None, prefix=cod)
        for cod in PERIODOS_ORDEM
    }
    if form.is_valid() and all(f.is_valid() for f in periodo_forms.values()):
        rotina = form.save()
        _salvar_periodos(rotina, periodo_forms, request)
        _processar_checklist_dia(request, rotina)
        messages.success(request, 'Rotina registrada!')
        return redirect('atividades:lista')
    return render(request, 'atividades/form.html', {
        'form': form, 'periodo_forms': periodo_forms,
        'periodo_labels': PERIODO_CHOICES, 'titulo': 'Registrar Rotina',
    })


@login_required
@perfil_required('administrador', 'enfermeiro')
def editar(request, pk):
    rotina = get_object_or_404(RotinaDiaria, pk=pk)
    form = RotinaDiariaForm(request.POST or None, instance=rotina)
    periodos_existentes = _preparar_periodos(rotina)
    periodo_forms = {
        cod: RotinaPeriodoForm(request.POST or None, instance=inst, prefix=cod)
        for cod, inst in periodos_existentes.items()
    }
    if form.is_valid() and all(f.is_valid() for f in periodo_forms.values()):
        form.save()
        _salvar_periodos(rotina, periodo_forms, request)
        _processar_checklist_dia(request, rotina)
        messages.success(request, 'Rotina atualizada!')
        return redirect('atividades:lista')
    return render(request, 'atividades/form.html', {
        'form': form, 'periodo_forms': periodo_forms,
        'periodo_labels': PERIODO_CHOICES, 'titulo': 'Editar Rotina',
    })


@login_required
def atividades_do_dia(request):
    """Endpoint AJAX: para um idoso numa data, retorna os itens de checklist
    de atividades personalizadas, e os medicamentos/consultas/fisioterapias
    programados, já separados por período (manhã/tarde/noite) e indicando
    o status salvo (se houver)."""
    idoso_id = request.GET.get('idoso')
    data_param = request.GET.get('data')
    vazio = {
        'items': [],
        'periodos': {cod: {'medicamentos': [], 'consultas': [], 'fisioterapias': []} for cod in PERIODOS_ORDEM},
    }
    if not idoso_id or not data_param:
        return JsonResponse(vazio)
    try:
        data_ref = datetime.strptime(data_param, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse(vazio)

    itens = itens_checklist_do_dia(idoso_id, data_ref)
    items = [{
        'id': item.id,
        'descricao': item.descricao,
        'checklist_titulo': item.checklist.titulo,
        'realizado': item.registro_do_dia.realizado if item.registro_do_dia else False,
        'observacoes': item.registro_do_dia.observacoes if item.registro_do_dia else '',
    } for item in itens]

    doses = medicamentos_do_dia(idoso_id, data_ref)
    consultas = consultas_do_dia(idoso_id, data_ref)
    fisios = sessoes_fisio_do_dia(idoso_id, data_ref)

    periodos = {}
    for cod in PERIODOS_ORDEM:
        periodos[cod] = {
            'medicamentos': [{
                'slot_key': f"{d['prescricao'].id}:{cod}:{d['horario'].strftime('%H%M')}",
                'medicamento': d['prescricao'].medicamento.nome,
                'dose': d['prescricao'].dose,
                'horario_previsto': d['horario'].strftime('%H:%M'),
                'horario_tomado': (
                    d['registro'].data_hora.strftime('%H:%M') if d['registro']
                    else d['horario'].strftime('%H:%M')
                ),
                'tomado': bool(d['registro'] and d['registro'].status == 'administrado'),
                'registro_id': d['registro'].id if d['registro'] else '',
                'status': d['registro'].get_status_display() if d['registro'] else 'Pendente',
            } for d in doses[cod]],
            'consultas': [{
                'id': c.id,
                'descricao': (
                    f"{c.data_hora:%H:%M} – {c.get_tipo_display()}"
                    + (f" – Dr(a). {c.medico.get_full_name()}" if c.medico else '')
                ),
                'realizada': c.status == 'realizada',
                'status': c.get_status_display(),
                'editavel': c.status in ('agendada', 'realizada'),
            } for c in consultas[cod]],
            'fisioterapias': [{
                'id': s.id,
                'descricao': f"{s.data_hora:%H:%M} – {s.objetivo or 'Sessão de fisioterapia'}",
                'realizada': s.status == 'realizada',
                'status': s.get_status_display(),
                'editavel': s.status in ('agendada', 'realizada'),
            } for s in fisios[cod]],
        }

    return JsonResponse({'items': items, 'periodos': periodos})


@login_required
@perfil_required('administrador', 'medico', 'enfermeiro', 'fisioterapeuta')
def checklist_lista(request, idoso_pk):
    from idosos.models import Idoso
    idoso = get_object_or_404(Idoso, pk=idoso_pk)
    checklists = idoso.checklists_atividades.prefetch_related('itens').order_by('-ativo', '-criado_em')
    return render(request, 'atividades/checklist_lista.html', {
        'idoso': idoso, 'checklists': checklists,
    })


@login_required
@perfil_required('administrador', 'medico', 'enfermeiro', 'fisioterapeuta')
def checklist_novo(request, idoso_pk):
    from idosos.models import Idoso
    idoso = get_object_or_404(Idoso, pk=idoso_pk)
    form = ChecklistAtividadeForm(request.POST or None)
    formset = ItemChecklistFormSet(request.POST or None, instance=ChecklistAtividade())
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        obj = form.save(commit=False)
        obj.idoso = idoso
        obj.prescrito_por = request.user
        obj.save()
        formset.instance = obj
        formset.save()
        messages.success(request, 'Checklist de atividades criada!')
        return redirect('idosos:detalhe', pk=idoso_pk)
    return render(request, 'atividades/checklist_form.html', {
        'form': form, 'formset': formset, 'idoso': idoso, 'titulo': 'Nova Checklist de Atividades'
    })


@login_required
@perfil_required('administrador', 'medico', 'enfermeiro', 'fisioterapeuta')
def checklist_editar(request, pk):
    checklist = get_object_or_404(ChecklistAtividade, pk=pk)
    form = ChecklistAtividadeForm(request.POST or None, instance=checklist)
    formset = ItemChecklistFormSet(request.POST or None, instance=checklist)
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        messages.success(request, 'Checklist atualizada!')
        return redirect('idosos:detalhe', pk=checklist.idoso_id)
    return render(request, 'atividades/checklist_form.html', {
        'form': form, 'formset': formset, 'idoso': checklist.idoso,
        'checklist': checklist, 'titulo': 'Editar Checklist de Atividades'
    })


@login_required
@perfil_required('administrador', 'medico', 'enfermeiro', 'fisioterapeuta')
def checklist_encerrar(request, pk):
    checklist = get_object_or_404(ChecklistAtividade, pk=pk)
    if request.method == 'POST':
        checklist.ativo = False
        checklist.save(update_fields=['ativo'])
        messages.success(request, 'Checklist encerrada.')
        return redirect('idosos:detalhe', pk=checklist.idoso_id)
    return render(request, 'atividades/confirmar_encerrar_checklist.html', {'checklist': checklist})


@login_required
@perfil_required('administrador')
def excluir(request, pk):
    rotina = get_object_or_404(RotinaDiaria, pk=pk)
    if request.method == 'POST':
        rotina.delete()
        return redirect('atividades:lista')
    return render(request, 'atividades/confirmar_exclusao.html', {'rotina': rotina})
