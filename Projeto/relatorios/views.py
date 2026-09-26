from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from datetime import date, timedelta
from core.decorators import perfil_required

try:
    from xhtml2pdf import pisa
    from io import BytesIO
    PDF_OK = True
except ImportError:
    PDF_OK = False


def _pdf_response(html_string, filename):
    if not PDF_OK:
        return HttpResponse(
            "xhtml2pdf não instalado. Execute: pip install xhtml2pdf",
            content_type='text/plain'
        )
    result = BytesIO()
    pdf = pisa.CreatePDF(html_string.encode('utf-8'), dest=result)
    if pdf.err:
        return HttpResponse('Erro ao gerar PDF.', content_type='text/plain')
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


# ── Dashboard de relatórios ───────────────────────────────────────────────────

@login_required
def lista(request):
    return render(request, 'relatorios/lista.html')


# ── Relatório para Familiar ───────────────────────────────────────────────────

@login_required
def familiar_relatorio(request):
    if not request.user.is_familiar:
        return redirect('relatorios:lista')
    from idosos.models import Idoso, FamiliarVinculo
    from medicamentos.models import PrescricaoMedicamento, RegistroAdministracao
    from fisioterapia.models import SessaoFisioterapia
    from atividades.models import RotinaDiaria
    from consultas.models import Consulta

    hoje = date.today()
    idosos_ids = FamiliarVinculo.objects.filter(
        familiar=request.user).values_list('idoso_id', flat=True)
    idosos = Idoso.objects.filter(id__in=idosos_ids)
    inicio = request.GET.get('inicio', str(hoje - timedelta(days=30)))
    fim = request.GET.get('fim', str(hoje))

    ctx = {
        'idosos': idosos,
        'consultas': Consulta.objects.filter(
            idoso__in=idosos_ids, data_hora__date__range=[inicio, fim]
        ).select_related('idoso', 'medico').order_by('-data_hora'),
        'prescricoes': PrescricaoMedicamento.objects.filter(
            idoso__in=idosos_ids, ativa=True
        ).select_related('idoso', 'medicamento', 'prescrito_por'),
        'administracoes': RegistroAdministracao.objects.filter(
            prescricao__idoso__in=idosos_ids,
            data_hora__date__range=[inicio, fim]
        ).select_related('prescricao__idoso', 'prescricao__medicamento', 'administrado_por').order_by('-data_hora'),
        'sessoes': SessaoFisioterapia.objects.filter(
            idoso__in=idosos_ids, data_hora__date__range=[inicio, fim]
        ).select_related('idoso', 'fisioterapeuta').order_by('-data_hora'),
        'rotinas': RotinaDiaria.objects.filter(
            idoso__in=idosos_ids, data__range=[inicio, fim]
        ).select_related('idoso').prefetch_related('periodos').order_by('-data'),
        'inicio': inicio, 'fim': fim, 'hoje': hoje,
    }
    if request.GET.get('pdf'):
        html = render_to_string('relatorios/pdf/familiar.html', ctx)
        return _pdf_response(html, 'relatorio_familiar.pdf')
    return render(request, 'relatorios/familiar.html', ctx)


# ── Relatório de Idosos ───────────────────────────────────────────────────────

@login_required
@perfil_required('administrador', 'medico', 'recepcionista')
def idosos_relatorio(request):
    from idosos.models import Idoso
    idosos = Idoso.objects.all().order_by('nome')
    ctx = {'idosos': idosos, 'hoje': date.today()}
    if request.GET.get('pdf'):
        html = render_to_string('relatorios/pdf/idosos.html', ctx)
        return _pdf_response(html, 'relatorio_idosos.pdf')
    return render(request, 'relatorios/idosos.html', ctx)


# ── Relatório de Medicamentos ─────────────────────────────────────────────────

@login_required
@perfil_required('administrador', 'medico', 'enfermeiro')
def medicamentos_relatorio(request):
    from medicamentos.models import Medicamento, RegistroAdministracao
    hoje = date.today()
    inicio = hoje - timedelta(days=30)
    alertas = Medicamento.objects.filter(estoque_atual__lte=10, ativo=True)
    registros = RegistroAdministracao.objects.filter(
        data_hora__date__gte=inicio
    ).select_related('prescricao__idoso', 'prescricao__medicamento', 'administrado_por')
    ctx = {'alertas': alertas, 'registros': registros, 'hoje': hoje}
    if request.GET.get('pdf'):
        html = render_to_string('relatorios/pdf/medicamentos.html', ctx)
        return _pdf_response(html, 'relatorio_medicamentos.pdf')
    return render(request, 'relatorios/medicamentos.html', ctx)


# ── Relatório de Consultas ────────────────────────────────────────────────────

@login_required
@perfil_required('administrador', 'medico', 'recepcionista')
def consultas_relatorio(request):
    from consultas.models import Consulta
    hoje = date.today()
    inicio = request.GET.get('inicio', str(hoje - timedelta(days=30)))
    fim = request.GET.get('fim', str(hoje))
    consultas = Consulta.objects.filter(
        data_hora__date__range=[inicio, fim]
    ).select_related('idoso', 'medico').order_by('-data_hora')
    ctx = {'consultas': consultas, 'inicio': inicio, 'fim': fim, 'hoje': hoje}
    if request.GET.get('pdf'):
        html = render_to_string('relatorios/pdf/consultas.html', ctx)
        return _pdf_response(html, 'relatorio_consultas.pdf')
    return render(request, 'relatorios/consultas.html', ctx)


# ── Relatório de Fisioterapia ─────────────────────────────────────────────────

@login_required
@perfil_required('administrador', 'medico', 'fisioterapeuta')
def fisioterapia_relatorio(request):
    from fisioterapia.models import SessaoFisioterapia
    hoje = date.today()
    sessoes = SessaoFisioterapia.objects.select_related(
        'idoso', 'fisioterapeuta', 'autorizado_por'
    ).order_by('-data_hora')[:100]
    pendentes = SessaoFisioterapia.objects.filter(autorizada=False, status='agendada')
    ctx = {'sessoes': sessoes, 'pendentes': pendentes, 'hoje': hoje}
    if request.GET.get('pdf'):
        html = render_to_string('relatorios/pdf/fisioterapia.html', ctx)
        return _pdf_response(html, 'relatorio_fisioterapia.pdf')
    return render(request, 'relatorios/fisioterapia.html', ctx)


# ── Relatório de Atividades ───────────────────────────────────────────────────

@login_required
@perfil_required('administrador', 'enfermeiro', 'recepcionista')
def atividades_relatorio(request):
    from atividades.models import RotinaDiaria
    hoje = date.today()
    data_filtro = request.GET.get('data', str(hoje))
    rotinas = RotinaDiaria.objects.filter(
        data=data_filtro
    ).select_related('idoso').prefetch_related('periodos').order_by('idoso__nome')
    ctx = {'rotinas': rotinas, 'data_filtro': data_filtro, 'hoje': hoje}
    if request.GET.get('pdf'):
        html = render_to_string('relatorios/pdf/atividades.html', ctx)
        return _pdf_response(html, f'relatorio_atividades_{data_filtro}.pdf')
    return render(request, 'relatorios/atividades.html', ctx)
