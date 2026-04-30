# EduFlow AI

Back-end automation platform for academic operations, replacing manual SQL updates with secure APIs, audit logs, role-based access control and AI-assisted request analysis.

## Sobre o projeto

O EduFlow AI simula uma plataforma interna de backoffice academico para instituicoes de ensino. A proposta e substituir alteracoes manuais no banco de dados por fluxos seguros via API, com validacao de regras de negocio, controle de acesso, auditoria e apoio de IA para triagem administrativa.

O projeto foi construido para portfolio backend Python, automacao, dados e IA aplicada. A interface React funciona como vitrine do produto, mas o nucleo tecnico esta no backend Python.

## Problema

Em muitas operacoes internas, mudancas criticas ainda sao feitas manualmente via SQL, como:

- alteracao de status de aluno;
- criacao ou bloqueio de matricula;
- revisao financeira;
- cancelamento de solicitacoes;
- ajustes em dados sensiveis sem trilha de auditoria.

Esse processo aumenta risco operacional, dificulta rastreabilidade e fragiliza a seguranca.

## Solucao

O EduFlow AI centraliza essas alteracoes em uma API REST segura. Toda acao critica passa por:

- autenticacao JWT;
- perfis de acesso;
- validacoes do Safe Change Engine;
- persistencia relacional com SQLAlchemy 2.0;
- logs de auditoria;
- analise opcional por IA generativa.

## Principais funcionalidades

- Login com JWT.
- Perfis `admin`, `operator` e `viewer`.
- Cadastro e consulta de alunos.
- CPF com mascara `000.000.000-00` e validacao de exatamente 11 digitos.
- Cadastro e consulta de cursos.
- Criacao e controle de matriculas.
- Bloqueio de alteracoes perigosas por regra de negocio.
- Solicitacoes administrativas com fluxo de revisao.
- Analise de solicitacoes com OpenAI API ou fallback local.
- Auditoria para alteracoes criticas.
- Frontend React em Portugues BR.
- Docker Compose com PostgreSQL, API e frontend.
- Testes automatizados com Pytest.

## Onde Python esta presente

Python e o centro do projeto:

- API FastAPI em `app/main.py`;
- rotas REST em `app/api/routes`;
- autenticacao e seguranca em `app/core`;
- modelos SQLAlchemy 2.0 em `app/models`;
- schemas Pydantic v2 em `app/schemas`;
- regras de negocio em `app/services`;
- Safe Change Engine em `app/services/safe_change_service.py`;
- auditoria em `app/services/audit_service.py`;
- integracao com IA em `app/services/ai_service.py`;
- seed do banco em `app/db/seed.py`;
- testes em `app/tests`.

O React consome essa API Python e apresenta a experiencia visual do produto.

## Tecnologias

### Backend

- Python 3.14 no Docker, estruturado para Python moderno
- FastAPI
- Uvicorn
- PostgreSQL 16
- SQLAlchemy 2.0
- Alembic
- Pydantic v2
- JWT com `python-jose`
- Passlib/bcrypt
- OpenAI API
- Pytest

### Frontend

- React
- Vite
- TypeScript
- Lucide React
- CSS responsivo customizado

### Infra

- Docker
- Docker Compose
- PostgreSQL containerizado

## Arquitetura

```text
eduflow-ai/
├── app/
│   ├── api/routes/                  # Endpoints REST
│   ├── core/                        # Configuracao, seguranca e permissoes
│   ├── db/                          # Conexao, metadata e seed
│   ├── models/                      # Modelos SQLAlchemy
│   ├── repositories/                # Acesso a dados
│   ├── schemas/                     # Contratos Pydantic
│   ├── services/                    # Regras de negocio, IA e auditoria
│   └── tests/                       # Testes automatizados
├── frontend/                        # Interface React
├── streamlit_app/                   # Dashboard legado opcional
├── alembic/                         # Migrations
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Modelo de dados

Entidades principais:

- `users`: usuarios internos e perfis.
- `students`: alunos e status academico.
- `courses`: cursos.
- `enrollments`: matriculas e status financeiro.
- `administrative_requests`: solicitacoes administrativas.
- `ai_request_analysis`: analises geradas por IA.
- `audit_logs`: trilha de auditoria.

## Regras de negocio

- Admin pode gerenciar usuarios e consultar auditoria.
- Operator pode criar e alterar dados operacionais.
- Viewer pode apenas consultar.
- Aluno bloqueado nao pode receber matricula.
- Curso inativo nao aceita matricula.
- Matricula nao pode ser ativada com pagamento vencido.
- Matricula concluida nao pode ser cancelada.
- CPF deve conter exatamente 11 digitos reais.
- E-mail e CPF duplicados retornam erro claro.

## Safe Change Engine

O Safe Change Engine centraliza regras que evitam alteracoes perigosas no banco. Ele representa o diferencial do projeto: trocar updates manuais por validacoes aplicacionais rastreaveis.

Arquivo principal:

```text
app/services/safe_change_service.py
```

Funcoes principais:

- `validate_student_status_change`
- `validate_enrollment_creation`
- `validate_enrollment_status_change`
- `validate_payment_status_change`
- `validate_request_status_transition`

## Auditoria

Alteracoes criticas geram registros em `audit_logs`, incluindo:

- usuario;
- acao;
- entidade;
- registro afetado;
- valor antigo;
- novo valor;
- motivo;
- data.

Exemplos de acoes auditadas:

- `student_status_changed`
- `course_status_changed`
- `enrollment_created`
- `enrollment_status_changed`
- `payment_status_changed`
- `request_created`
- `request_approved`
- `request_rejected`
- `ai_analysis_created`

## IA aplicada

O endpoint abaixo analisa uma solicitacao administrativa:

```http
POST /requests/{request_id}/ai-analysis
```

Retorno esperado:

```json
{
  "predicted_category": "financial_review",
  "priority": "high",
  "summary": "Aluno solicita revisao de cobranca possivelmente indevida.",
  "suggested_action": "Encaminhar para analise financeira.",
  "risk_level": "medium",
  "model_used": "gpt-4o-mini"
}
```

Se `OPENAI_API_KEY` nao estiver configurada, o sistema usa fallback local para nao quebrar o ambiente de desenvolvimento.

## Como rodar com Docker

```bash
docker compose up --build
```

Servicos:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Frontend React: `http://localhost:5173`
- PostgreSQL: `localhost:5432`

Na subida, a API executa:

```bash
alembic upgrade head
python -m app.db.seed
```

## Como rodar localmente

Backend:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Variaveis de ambiente

Crie um arquivo `.env` baseado em `.env.example`.

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/eduflow
SECRET_KEY=change_this_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_CHAT_MODEL=gpt-4o-mini
ENVIRONMENT=development
VITE_API_URL=http://localhost:8000
```

## Credenciais locais

Criadas pelo seed:

- `admin@eduflow.ai` / `admin123`
- `operator@eduflow.ai` / `operator123`
- `viewer@eduflow.ai` / `viewer123`

Essas credenciais sao apenas para ambiente local.

## Endpoints principais

- `GET /health`
- `POST /auth/login`
- `GET /users/me`
- `POST /users`
- `POST /students`
- `GET /students`
- `PATCH /students/{student_id}/status`
- `POST /courses`
- `GET /courses`
- `POST /enrollments`
- `PATCH /enrollments/{enrollment_id}/status`
- `PATCH /enrollments/{enrollment_id}/payment-status`
- `POST /requests`
- `PATCH /requests/{request_id}/start-review`
- `PATCH /requests/{request_id}/approve`
- `PATCH /requests/{request_id}/reject`
- `PATCH /requests/{request_id}/complete`
- `POST /requests/{request_id}/ai-analysis`
- `GET /audit-logs`

## Testes

Rode:

```bash
pytest
```

Ou dentro do container:

```bash
docker compose exec api pytest
```

Ultima validacao local:

```text
12 passed
```

## Frontend

O frontend React foi criado para ser a experiencia principal do produto. Ele inclui:

- tela de login;
- painel com metricas;
- cadastros de alunos, cursos, matriculas e solicitacoes;
- mascara e validacao de CPF;
- area de analise com IA;
- auditoria para usuarios admin;
- interface em Portugues BR;
- visual leve, colorido e profissional.

## Roadmap

- RAG com politicas academicas.
- Integracao com n8n.
- Notificacoes automaticas.
- Relatorios em PDF.
- Deploy em cloud.
- Testes de carga.
- CI/CD.
- Suite de testes frontend.

## O que este projeto demonstra

- Arquitetura backend Python limpa.
- Separacao entre rotas, servicos, schemas, modelos e repositorios.
- Regras de negocio fora das rotas.
- Validacao de dados com Pydantic.
- Persistencia relacional com SQLAlchemy 2.0.
- Uso pratico de IA generativa.
- Frontend consumindo uma API real.
- Dockerizacao de uma aplicacao full stack.
