from datetime import date


def notificacoes(request):
    if not request.user.is_authenticated:
        return {}

    user = request.user
    notifs = []

    try:
        if user.is_administrador or user.is_medico or user.is_enfermeiro:
            from medicamentos.models import Medicamento
            from django.db.models import F
            count = Medicamento.objects.filter(
                estoque_atual__lte=F('estoque_minimo'), ativo=True).count()
            if count:
                notifs.append({
                    'tipo': 'danger',
                    'icone': 'capsule-pill',
                    'texto': f'{count} medicamento(s) com estoque baixo',
                    'url': 'medicamentos:lista',
                })

        if user.is_administrador or user.is_medico or user.is_recepcionista:
            from consultas.models import Consulta
            hoje = date.today()
            count = Consulta.objects.filter(data_hora__date=hoje, status='agendada').count()
            if count:
                notifs.append({
                    'tipo': 'info',
                    'icone': 'clipboard2-pulse',
                    'texto': f'{count} consulta(s) agendada(s) hoje',
                    'url': 'consultas:lista',
                })

        if user.is_administrador or user.is_medico:
            from fisioterapia.models import SessaoFisioterapia
            count = SessaoFisioterapia.objects.filter(
                autorizada=False, status='agendada').count()
            if count:
                notifs.append({
                    'tipo': 'warning',
                    'icone': 'activity',
                    'texto': f'{count} sessão(ões) aguardando autorização',
                    'url': 'fisioterapia:lista',
                })

        if user.is_fisioterapeuta:
            from fisioterapia.models import SessaoFisioterapia
            hoje = date.today()
            count = SessaoFisioterapia.objects.filter(
                fisioterapeuta=user, data_hora__date=hoje,
                autorizada=True, status='agendada').count()
            if count:
                notifs.append({
                    'tipo': 'success',
                    'icone': 'activity',
                    'texto': f'{count} sessão(ões) de fisioterapia hoje',
                    'url': 'fisioterapia:lista',
                })

        if user.is_familiar:
            from idosos.models import FamiliarVinculo
            from consultas.models import Consulta
            hoje = date.today()
            idosos_ids = FamiliarVinculo.objects.filter(
                familiar=user).values_list('idoso_id', flat=True)
            count = Consulta.objects.filter(
                idoso__in=idosos_ids, data_hora__date=hoje, status='agendada').count()
            if count:
                notifs.append({
                    'tipo': 'info',
                    'icone': 'clipboard2-pulse',
                    'texto': f'{count} consulta(s) de seu familiar hoje',
                    'url': 'consultas:lista',
                })

    except Exception:
        pass

    return {
        'notificacoes': notifs,
        'notif_count': len(notifs),
    }
