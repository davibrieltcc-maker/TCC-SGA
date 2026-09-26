# Sobrescreve os formatos do locale pt-BR do Django.
#
# Motivo: os widgets HTML5 <input type="date"> e <input type="datetime-local">
# exigem valor no formato ISO (YYYY-MM-DD / YYYY-MM-DDTHH:MM). O locale pt-BR
# padrao do Django renderiza a data como DD/MM/AAAA, o que faz o navegador
# exibir o campo VAZIO ao editar um registro ja salvo. Colocando o formato ISO
# em primeiro lugar, a renderizacao passa a funcionar e os formatos BR
# continuam sendo aceitos no envio do formulario.

DATE_INPUT_FORMATS = [
    "%Y-%m-%d",   # 2026-09-10  (HTML5 <input type="date">)
    "%d/%m/%Y",   # 10/09/2026
    "%d/%m/%y",   # 10/09/26
]

DATETIME_INPUT_FORMATS = [
    "%Y-%m-%dT%H:%M",       # 2026-09-10T14:30  (HTML5 <input type="datetime-local">)
    "%Y-%m-%dT%H:%M:%S",    # 2026-09-10T14:30:00
    "%Y-%m-%d %H:%M:%S",    # 2026-09-10 14:30:00
    "%Y-%m-%d %H:%M",       # 2026-09-10 14:30
    "%d/%m/%Y %H:%M:%S",    # 10/09/2026 14:30:00
    "%d/%m/%Y %H:%M",       # 10/09/2026 14:30
]

TIME_INPUT_FORMATS = [
    "%H:%M",     # 14:30  (HTML5 <input type="time">)
    "%H:%M:%S",
]
