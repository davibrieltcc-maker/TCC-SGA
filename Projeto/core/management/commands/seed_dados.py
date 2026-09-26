"""
Limpa toda a base de dados (mantendo apenas os administradores) e a
repopula com um conjunto completo e realista de dados de exemplo,
cobrindo idosos, funcionários, familiares, medicamentos, prescrições,
consultas, fisioterapia, rotinas diárias e checklists.

Execute: python manage.py seed_dados
"""
import random
from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone


NOMES_M = [
    'João', 'José', 'Antônio', 'Francisco', 'Carlos', 'Paulo', 'Pedro',
    'Sebastião', 'Raimundo', 'Osvaldo', 'Geraldo', 'Manoel', 'Ricardo',
    'Eduardo', 'Roberto', 'Marcelo', 'Fernando', 'Wagner', 'Gilberto', 'André',
]
NOMES_F = [
    'Maria', 'Ana', 'Francisca', 'Antônia', 'Adriana', 'Juliana', 'Márcia',
    'Fernanda', 'Patrícia', 'Aline', 'Sandra', 'Camila', 'Vera', 'Rosa',
    'Terezinha', 'Cecília', 'Beatriz', 'Sônia', 'Eliane', 'Simone',
]
SOBRENOMES = [
    'Silva', 'Santos', 'Oliveira', 'Souza', 'Rodrigues', 'Ferreira', 'Alves',
    'Pereira', 'Lima', 'Gomes', 'Costa', 'Ribeiro', 'Martins', 'Carvalho',
    'Almeida', 'Lopes', 'Soares', 'Fernandes', 'Vieira', 'Barbosa', 'Nunes',
    'Teixeira', 'Correia', 'Cavalcante', 'Moura',
]
CIDADES_ESTADOS = [
    ('Fortaleza', 'CE'), ('São Paulo', 'SP'), ('Rio de Janeiro', 'RJ'),
    ('Belo Horizonte', 'MG'), ('Recife', 'PE'), ('Salvador', 'BA'),
    ('Curitiba', 'PR'), ('Porto Alegre', 'RS'), ('Manaus', 'AM'),
]
RUAS = [
    'Rua das Flores', 'Av. Beira-Mar', 'Rua Dom Pedro II', 'Rua da Paz',
    'Av. Presidente Vargas', 'Rua Sete de Setembro', 'Rua do Rosário',
    'Av. Duque de Caxias', 'Rua São José', 'Rua das Palmeiras',
]
CONDICOES_MEDICAS = [
    'Hipertensão arterial sistêmica', 'Diabetes mellitus tipo 2',
    'Artrite reumatoide', 'Osteoporose', 'Doença de Alzheimer (fase leve)',
    'Doença de Parkinson', 'Insuficiência cardíaca compensada',
    'Doença pulmonar obstrutiva crônica (DPOC)', 'Depressão',
    'Ansiedade generalizada', 'Hipotireoidismo', 'Osteoartrose de joelhos',
]
ALERGIAS = [
    'Dipirona', 'Penicilina', 'Nenhuma conhecida', 'Frutos do mar', 'Látex',
    'Sulfa', 'Ácaro/poeira', 'Nenhuma conhecida',
]
TIPOS_SANGUINEOS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
PARENTESCOS = ['Filho(a)', 'Neto(a)', 'Sobrinho(a)', 'Cônjuge', 'Irmão(ã)', 'Sobrinho(a)']

MEDICAMENTOS_CATALOGO = [
    ('Losartana Potássica 50mg', 'Losartana potássica', 'Medley', 'comprimido'),
    ('Metformina 850mg', 'Metformina', 'EMS', 'comprimido'),
    ('Sinvastatina 20mg', 'Sinvastatina', 'Neo Química', 'comprimido'),
    ('AAS 100mg', 'Ácido acetilsalicílico', 'Bayer', 'comprimido'),
    ('Omeprazol 20mg', 'Omeprazol', 'EMS', 'cápsula'),
    ('Bromazepam 3mg', 'Bromazepam', 'Neo Química', 'comprimido'),
    ('Paracetamol 750mg', 'Paracetamol', 'EMS', 'comprimido'),
    ('Levotiroxina 50mcg', 'Levotiroxina sódica', 'Merck', 'comprimido'),
    ('Furosemida 40mg', 'Furosemida', 'EMS', 'comprimido'),
    ('Enalapril 10mg', 'Maleato de enalapril', 'EMS', 'comprimido'),
    ('Sertralina 50mg', 'Sertralina', 'EMS', 'comprimido'),
    ('Carbonato de Cálcio 500mg', 'Carbonato de cálcio', 'EMS', 'comprimido'),
    ('Ácido Fólico 5mg', 'Ácido fólico', 'EMS', 'comprimido'),
    ('Clonazepam 2mg', 'Clonazepam', 'Roche', 'comprimido'),
    ('Anlodipino 5mg', 'Besilato de anlodipino', 'EMS', 'comprimido'),
]

ESPECIALIDADES_MEDICO = ['Geriatria', 'Clínica Médica', 'Cardiologia']
ESPECIALIDADES_FISIO = ['Fisioterapia Geriátrica', 'Fisioterapia Ortopédica', 'Fisioterapia Respiratória']

FREQUENCIAS_HORARIOS = {
    '1x_dia': '08:00',
    '2x_dia': '08:00, 20:00',
    '3x_dia': '08:00, 14:00, 20:00',
    'cada_8h': '06:00, 14:00, 22:00',
    'cada_12h': '08:00, 20:00',
}

EXERCICIOS_FISIO = [
    'Alongamento de membros inferiores, fortalecimento de quadríceps e treino de equilíbrio.',
    'Exercícios respiratórios, mobilização articular e caminhada assistida.',
    'Fortalecimento de membros superiores e treino de marcha com apoio.',
]


class Command(BaseCommand):
    help = 'Limpa toda a base (exceto administradores) e recria dados de exemplo completos.'

    def add_arguments(self, parser):
        parser.add_argument('--senha', default='Asilo@2026',
                             help='Senha padrão para todos os usuários criados.')

    def handle(self, *args, **options):
        senha = options['senha']
        random.seed(20260926)
        with transaction.atomic():
            self._limpar()
            self._popular(senha)
        self.stdout.write(self.style.SUCCESS('Base de dados recriada com sucesso!'))
        self.stdout.write(self.style.WARNING(
            f'Todos os novos usuários (funcionários e familiares) usam a senha: {senha}'
        ))

    # ── Limpeza ──────────────────────────────────────────────────────────
    def _limpar(self):
        from atividades.models import HorarioAtividade
        from medicamentos.models import Medicamento
        from idosos.models import Idoso
        from core.models import Usuario

        Idoso.objects.all().delete()  # cascateia rotinas, prescrições, consultas, fisio, checklists…
        Medicamento.objects.all().delete()
        HorarioAtividade.objects.all().delete()
        Usuario.objects.exclude(perfil='administrador').exclude(is_superuser=True).delete()

    # ── População ────────────────────────────────────────────────────────
    def _popular(self, senha):
        nomes_usados = set()

        def nome_unico(lista_nomes):
            while True:
                nome = f"{random.choice(lista_nomes)} {random.choice(SOBRENOMES)} {random.choice(SOBRENOMES)}"
                if nome not in nomes_usados:
                    nomes_usados.add(nome)
                    return nome

        def cpf_fake(n):
            return f"{100 + n:03d}.{200 + n:03d}.{300 + n:03d}-{n % 100:02d}"

        contador_cpf = [0]

        def proximo_cpf():
            contador_cpf[0] += 1
            return cpf_fake(contador_cpf[0])

        hoje = date.today()

        # ── Funcionários ─────────────────────────────────────────────
        from core.models import Usuario
        from funcionarios.models import Funcionario

        def criar_funcionario(username, perfil, sexo, registro_prof, especialidade, admissao_dias_atras):
            nome_completo = nome_unico(NOMES_M if sexo == 'M' else NOMES_F)
            primeiro, *resto = nome_completo.split(' ')
            sobrenome = ' '.join(resto)
            usuario = Usuario.objects.create_user(
                username=username,
                email=f"{username}@asilo.com",
                password=senha,
                first_name=primeiro,
                last_name=sobrenome,
                perfil=perfil,
                telefone=f"(85) 9{random.randint(8000,9999)}-{random.randint(1000,9999)}",
                cpf=proximo_cpf(),
                data_nascimento=hoje - timedelta(days=random.randint(25*365, 55*365)),
                especialidade=especialidade,
                data_admissao=hoje - timedelta(days=admissao_dias_atras),
                primeiro_acesso=False,
                ativo=True,
            )
            Funcionario.objects.create(
                usuario=usuario,
                registro_profissional=registro_prof,
                especialidade=especialidade,
                vinculo='clt',
                data_admissao=usuario.data_admissao,
                salario=random.choice([2200, 2800, 3500, 4500, 6500]),
                carga_horaria=random.choice([30, 36, 44]),
                turno=random.choice(['Manhã', 'Tarde', 'Noite', 'Integral']),
                observacoes='Funcionário(a) dedicado(a), sem ocorrências disciplinares.',
            )
            return usuario

        medicos = [
            criar_funcionario('dra.helena', 'medico', 'F', 'CRM-CE 12345', 'Geriatria', 900),
            criar_funcionario('dr.ricardo', 'medico', 'M', 'CRM-CE 23456', 'Clínica Médica', 600),
        ]
        enfermeiros = [
            criar_funcionario('enf.camila', 'enfermeiro', 'F', 'COREN-CE 34567', '', 700),
            criar_funcionario('enf.thiago', 'enfermeiro', 'M', 'COREN-CE 45678', '', 400),
        ]
        fisioterapeutas = [
            criar_funcionario('fisio.renata', 'fisioterapeuta', 'F', 'CREFITO-CE 56789', 'Fisioterapia Geriátrica', 500),
            criar_funcionario('fisio.diego', 'fisioterapeuta', 'M', 'CREFITO-CE 67890', 'Fisioterapia Ortopédica', 300),
        ]
        recepcionistas = [
            criar_funcionario('recep.larissa', 'recepcionista', 'F', '', '', 800),
            criar_funcionario('recep.bruno', 'recepcionista', 'M', '', '', 200),
        ]

        # ── Familiares ───────────────────────────────────────────────
        familiares = []
        for i in range(14):
            sexo = 'M' if i % 2 == 0 else 'F'
            nome_completo = nome_unico(NOMES_M if sexo == 'M' else NOMES_F)
            primeiro, *resto = nome_completo.split(' ')
            username = f"fam.{primeiro.lower()}{i}"
            usuario = Usuario.objects.create_user(
                username=username,
                email=f"{username}@email.com",
                password=senha,
                first_name=primeiro,
                last_name=' '.join(resto),
                perfil='familiar',
                telefone=f"(85) 9{random.randint(8000,9999)}-{random.randint(1000,9999)}",
                cpf=proximo_cpf(),
                data_nascimento=hoje - timedelta(days=random.randint(25*365, 60*365)),
                primeiro_acesso=False,
                ativo=True,
            )
            familiares.append(usuario)

        # ── Medicamentos (catálogo) ────────────────────────────────────
        from medicamentos.models import Medicamento
        medicamentos = []
        for nome, principio, fabricante, forma in MEDICAMENTOS_CATALOGO:
            medicamentos.append(Medicamento.objects.create(
                nome=nome, principio_ativo=principio, fabricante=fabricante, forma=forma,
                estoque_atual=random.randint(5, 200), estoque_minimo=20, unidade='unidade',
                observacoes='Manter em local seco e ao abrigo da luz.', ativo=True,
            ))

        # ── Idosos ───────────────────────────────────────────────────
        from idosos.models import Idoso, FamiliarVinculo
        idosos = []
        for i in range(14):
            sexo = 'M' if i % 2 == 0 else 'F'
            nome_completo = nome_unico(NOMES_M if sexo == 'M' else NOMES_F)
            cidade, estado = random.choice(CIDADES_ESTADOS)
            idoso = Idoso.objects.create(
                nome=nome_completo,
                data_nascimento=hoje - timedelta(days=random.randint(65*365, 95*365)),
                sexo=sexo,
                cpf=proximo_cpf(),
                rg=f"{random.randint(1000000,9999999)}-{random.randint(0,9)}",
                tipo_sanguineo=random.choice(TIPOS_SANGUINEOS),
                status='ativo',
                endereco=f"{random.choice(RUAS)}, {random.randint(10, 2000)}",
                cidade=cidade, estado=estado,
                cep=f"{random.randint(10000,99999)}-{random.randint(100,999)}",
                alergias=random.choice(ALERGIAS),
                condicoes_medicas=', '.join(random.sample(CONDICOES_MEDICAS, k=random.randint(1, 3))),
                observacoes='Idoso(a) colaborativo(a), participa bem das atividades propostas pela equipe.',
                data_entrada=hoje - timedelta(days=random.randint(30, 1500)),
                numero_quarto=f"{100 + i}",
            )
            idosos.append(idoso)

        # ── Vínculos familiares ──────────────────────────────────────
        fam_pool = list(familiares)
        for idoso in idosos:
            qtd = random.choice([1, 1, 2])
            escolhidos = random.sample(fam_pool, k=min(qtd, len(fam_pool)))
            for j, familiar in enumerate(escolhidos):
                FamiliarVinculo.objects.create(
                    familiar=familiar, idoso=idoso,
                    parentesco=random.choice(PARENTESCOS),
                    contato_principal=(j == 0),
                )

        # ── Prontuários + Consultas ────────────────────────────────────
        from consultas.models import Consulta, Prontuario
        for idoso in idosos:
            Prontuario.objects.create(
                idoso=idoso,
                historico_familiar='Pais hipertensos; histórico familiar de diabetes tipo 2.',
                historico_pessoal='Sem cirurgias relevantes prévias além das listadas. Acompanhamento clínico regular.',
                cirurgias_anteriores=random.choice([
                    'Nenhuma cirurgia relatada.',
                    'Colecistectomia há 10 anos.',
                    'Prótese de quadril há 3 anos.',
                ]),
                vacinas='Influenza (anual), dT, Pneumocócica e COVID-19 em dia conforme calendário do idoso.',
            )
            medico = random.choice(medicos)
            data_passada = timezone.make_aware(datetime.combine(hoje - timedelta(days=random.randint(5, 60)), datetime.min.time().replace(hour=9)))
            Consulta.objects.create(
                idoso=idoso, medico=medico, data_hora=data_passada, tipo='rotina', status='realizada',
                queixa_principal='Consulta de acompanhamento de rotina.',
                anamnese='Paciente relata estar se alimentando bem e sem queixas agudas no período.',
                exame_fisico='Bom estado geral, ausculta cardiopulmonar sem alterações, sinais vitais estáveis.',
                diagnostico='Quadro clínico estável, condições crônicas controladas.',
                prescricao='Manter medicações de uso contínuo. Reforçar hidratação e atividade física leve.',
                retorno_em=data_passada.date() + timedelta(days=90),
                observacoes='Sem intercorrências.',
            )
            data_futura = timezone.make_aware(datetime.combine(hoje + timedelta(days=random.randint(2, 20)), datetime.min.time().replace(hour=10)))
            Consulta.objects.create(
                idoso=idoso, medico=medico, data_hora=data_futura, tipo='retorno', status='agendada',
                queixa_principal='Retorno de rotina para reavaliação clínica.',
                observacoes='Consulta agendada pela equipe de enfermagem.',
            )

        # ── Prescrições + Registros de administração ───────────────────
        from medicamentos.models import PrescricaoMedicamento, RegistroAdministracao
        for idoso in idosos:
            n_prescricoes = random.randint(2, 3)
            escolhidos = random.sample(medicamentos, k=n_prescricoes)
            for medicamento in escolhidos:
                frequencia = random.choice(list(FREQUENCIAS_HORARIOS.keys()))
                horarios = FREQUENCIAS_HORARIOS[frequencia]
                prescricao = PrescricaoMedicamento.objects.create(
                    idoso=idoso, medicamento=medicamento,
                    prescrito_por=random.choice(medicos),
                    dose=random.choice(['1 comprimido', '2 comprimidos', '1 cápsula', '10ml']),
                    frequencia=frequencia, horarios=horarios,
                    data_inicio=hoje - timedelta(days=random.randint(10, 200)),
                    data_fim=None,
                    via_administracao='Via oral',
                    observacoes='Administrar preferencialmente com alimentos.',
                    ativa=True,
                )
                horas = [h.strip() for h in horarios.split(',')]
                for dias_atras in range(2, 0, -1):
                    dia = hoje - timedelta(days=dias_atras)
                    for h_str in horas:
                        hh, mm = (int(x) for x in h_str.split(':'))
                        status = random.choices(
                            ['administrado', 'administrado', 'administrado', 'recusado', 'omitido'],
                            k=1,
                        )[0]
                        RegistroAdministracao.objects.create(
                            prescricao=prescricao,
                            administrado_por=random.choice(enfermeiros),
                            data_hora=timezone.make_aware(datetime.combine(dia, datetime.min.time().replace(hour=hh, minute=mm))),
                            status=status,
                            observacoes='' if status == 'administrado' else 'Registrado pela equipe de enfermagem do turno.',
                        )

        # ── Fisioterapia ────────────────────────────────────────────────
        from fisioterapia.models import SessaoFisioterapia, PlanoReabilitacao
        idosos_fisio = random.sample(idosos, k=9)
        for idoso in idosos_fisio:
            fisio = random.choice(fisioterapeutas)
            medico_autorizador = random.choice(medicos)
            PlanoReabilitacao.objects.create(
                idoso=idoso, fisioterapeuta=fisio,
                titulo=f"Plano de reabilitação funcional – {idoso.nome.split()[0]}",
                objetivo_geral='Melhorar mobilidade, equilíbrio e força muscular, prevenindo quedas.',
                exercicios=random.choice(EXERCICIOS_FISIO),
                frequencia_semanal=random.choice([2, 3]),
                data_inicio=hoje - timedelta(days=random.randint(20, 150)),
                data_previsao_fim=hoje + timedelta(days=random.randint(30, 120)),
                ativo=True,
            )
            data_passada = timezone.make_aware(datetime.combine(hoje - timedelta(days=random.randint(2, 10)), datetime.min.time().replace(hour=9)))
            SessaoFisioterapia.objects.create(
                idoso=idoso, fisioterapeuta=fisio, data_hora=data_passada, duracao_minutos=45,
                status='realizada', objetivo='Fortalecimento muscular e treino de equilíbrio.',
                procedimentos='Cinesioterapia ativa-assistida, exercícios de equilíbrio em barras paralelas.',
                evolucao='Paciente apresentou boa evolução, tolerou bem os exercícios propostos.',
                observacoes='Manter frequência semanal.',
                autorizada=True, autorizado_por=medico_autorizador,
                data_autorizacao=timezone.now() - timedelta(days=30),
            )
            data_futura = timezone.make_aware(datetime.combine(hoje + timedelta(days=random.randint(1, 10)), datetime.min.time().replace(hour=13)))
            SessaoFisioterapia.objects.create(
                idoso=idoso, fisioterapeuta=fisio, data_hora=data_futura, duracao_minutos=45,
                status='agendada', objetivo='Continuidade do plano de reabilitação.',
                autorizada=True, autorizado_por=medico_autorizador,
                data_autorizacao=timezone.now() - timedelta(days=30),
            )

        # ── Horários fixos de atividades ────────────────────────────────
        from atividades.models import HorarioAtividade
        from datetime import time as time_cls
        for titulo, tipo, horario in [
            ('Café da manhã', 'alimentacao', time_cls(7, 0)),
            ('Banho e higiene matinal', 'higiene', time_cls(8, 0)),
            ('Almoço', 'alimentacao', time_cls(12, 0)),
            ('Medicação da tarde', 'medicamento', time_cls(14, 0)),
            ('Fisioterapia', 'fisioterapia', time_cls(15, 0)),
            ('Atividade de lazer/recreação', 'lazer', time_cls(16, 30)),
            ('Jantar', 'alimentacao', time_cls(19, 0)),
        ]:
            HorarioAtividade.objects.create(
                titulo=titulo, tipo=tipo, horario=horario, dias_semana='todos',
                descricao=f"Atividade padrão de {titulo.lower()} realizada diariamente.", ativo=True,
            )

        # ── Checklists de atividades personalizadas ─────────────────────
        from atividades.models import ChecklistAtividade, ItemChecklist, RegistroItemChecklist
        atividades_extra = [
            'Caminhada assistida 20 minutos', 'Alongamento matinal', 'Roda de conversa/leitura',
            'Jogo de memória', 'Hidratação reforçada (min. 1,5L/dia)',
        ]
        for idoso in idosos:
            checklist = ChecklistAtividade.objects.create(
                idoso=idoso, titulo='Plano de atividades e estímulo cognitivo',
                descricao='Atividades complementares prescritas pela equipe multiprofissional.',
                dias_semana='seg,ter,qua,qui,sex,sab,dom',
                data_inicio=hoje - timedelta(days=30),
                data_fim=None,
                prescrito_por=random.choice(enfermeiros),
                ativo=True,
            )
            itens = []
            for ordem, descricao in enumerate(random.sample(atividades_extra, k=2)):
                itens.append(ItemChecklist.objects.create(checklist=checklist, descricao=descricao, ordem=ordem))
            for dias_atras in range(2, 0, -1):
                dia = hoje - timedelta(days=dias_atras)
                for item in itens:
                    RegistroItemChecklist.objects.create(
                        item=item, data=dia, realizado=random.choice([True, True, False]),
                        observacoes='Realizado conforme planejado.' if random.random() > 0.3 else '',
                        registrado_por=random.choice(enfermeiros),
                    )

        # ── Rotina diária (dividida em manhã/tarde/noite) ────────────────
        from atividades.models import RotinaDiaria, RotinaPeriodo
        for idoso in idosos:
            for dias_atras in range(2, -1, -1):
                dia = hoje - timedelta(days=dias_atras)
                rotina = RotinaDiaria.objects.create(
                    idoso=idoso, data=dia,
                    observacoes_gerais='Dia transcorreu sem intercorrências relevantes.',
                )
                for periodo in ['manha', 'tarde', 'noite']:
                    RotinaPeriodo.objects.create(
                        rotina=rotina, periodo=periodo,
                        responsavel=random.choice(enfermeiros),
                        banho_realizado=(periodo != 'noite'),
                        higiene_oral=True,
                        troca_roupa=(periodo == 'manha'),
                        curativo=False,
                        obs_higiene='Higienização realizada sem alterações na pele.',
                        refeicoes_realizadas={
                            'manha': 'Café da manhã, lanche da manhã',
                            'tarde': 'Almoço, lanche da tarde',
                            'noite': 'Jantar, ceia',
                        }[periodo],
                        aceitacao_alimentar=random.choice(['total', 'total', 'parcial']),
                        obs_alimentacao='Boa aceitação da dieta oferecida.',
                    )

        self.stdout.write(f"Funcionários: {len(medicos)+len(enfermeiros)+len(fisioterapeutas)+len(recepcionistas)}")
        self.stdout.write(f"Familiares: {len(familiares)}")
        self.stdout.write(f"Idosos: {len(idosos)}")
        self.stdout.write(f"Medicamentos no catálogo: {len(medicamentos)}")
