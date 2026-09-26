# SGA-Idosos — Sistema de Gestão e Acompanhamento de Idosos
**TCC — Instituto Federal do Paraná (IFPR) — Paranaguá**
Davi Marcelino da Silva | Gabriel Maletzke de Avelar

---

## Tecnologias
- Python 3.x + Django 4.x
- Banco de dados: SQLite (integrado ao Django)
- Frontend: HTML5, CSS3, Bootstrap 5, JavaScript
- PDF: WeasyPrint (`pip install weasyprint`)

---

## Instalação

```bash
# 1. Clone e entre na pasta
cd TCC-Gerenciamento-Asilo

# 2. Instale dependências
pip install django pillow weasyprint

# 3. Aplique as migrations
python manage.py migrate

# 4. Crie o superusuário (Administrador)
python manage.py createsuperuser

# 5. (Opcional) Crie usuários de demonstração
python manage.py criar_usuarios_demo

# 6. Rode o servidor
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

---

## Perfis de Usuário e Permissões

| Perfil          | Pode fazer                                                                 |
|-----------------|----------------------------------------------------------------------------|
| Administrador   | Acesso total ao sistema                                                    |
| Médico          | Saúde, consultas, medicamentos, **autoriza sessões de fisioterapia**       |
| Fisioterapeuta  | Cria sessões (aguarda autorização médica), registra evolução               |
| Enfermeiro(a)   | Administra medicamentos, registra atividades diárias                       |
| Recepcionista   | Cadastra idosos e usuários (exceto Admin), agenda consultas                |
| Familiar        | Somente visualização do seu idoso vinculado                                |

---

## Fluxo de Autorização de Fisioterapia (RN006)

```
Fisioterapeuta cria sessão
        ↓
  status: AGENDADA | autorizada: FALSE
        ↓
  Médico visualiza sessões pendentes
        ↓
  [Autoriza] → autorizada: TRUE → Fisioterapeuta executa e registra evolução
  [Rejeita]  → status: CANCELADA
```

---

## Primeiro Acesso de Usuário (RN008)

1. Admin ou Recepcionista cria o usuário **sem definir senha**
2. Na lista de usuários aparece: `⚠ Aguardando 1º acesso`
3. Usuário faz login → sistema redireciona para `/auth/definir-senha/`
4. Usuário define sua senha → acesso liberado ao dashboard

---

## Apps Django

| App           | Responsabilidade                                      |
|---------------|-------------------------------------------------------|
| core          | Autenticação, perfis, gestão de usuários, dashboard   |
| idosos        | Cadastro, prontuário, vínculo familiar                |
| medicamentos  | Prescrição, programação, administração, alertas       |
| consultas     | Agendamento, evolução clínica, exames                 |
| fisioterapia  | Sessões com fluxo de autorização médica               |
| atividades    | Higienização e alimentação com horários               |
| funcionarios  | Dados profissionais, turnos                           |
| relatorios    | Dashboard e geração de PDF por módulo                 |

---

## Migrations necessárias após atualização

```bash
python manage.py migrate core 0002_usuario_novos_campos
python manage.py migrate fisioterapia 0002_sessao_autorizacao
```
