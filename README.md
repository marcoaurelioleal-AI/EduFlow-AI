# EduFlow AI

Plataforma backend para automação de operações acadêmicas, substituindo alterações manuais via SQL por APIs seguras, trilhas de auditoria, controle de acesso por perfil e análise de solicitações com apoio de IA.

## Sobre o projeto

O EduFlow AI simula uma plataforma interna de backoffice acadêmico para instituições de ensino. A proposta é substituir alterações manuais no banco de dados por fluxos seguros via API, com validação de regras de negócio, controle de acesso, auditoria e apoio de IA para triagem administrativa.

O projeto foi construído para portfólio backend Python, automação, dados e IA aplicada. A interface React funciona como vitrine do produto, mas o núcleo técnico está no backend Python.

## Problema

Em muitas operações internas, mudanças críticas ainda são feitas manualmente via SQL, como:

- alteração de status de aluno;
- criação ou bloqueio de matrícula;
- revisão financeira;
- cancelamento de solicitações;
- ajustes em dados sensíveis sem trilha de auditoria.

Esse processo aumenta o risco operacional, dificulta a rastreabilidade e fragiliza a segurança.

## Solução

O EduFlow AI centraliza essas alterações em uma API REST segura. Toda ação crítica passa por:

- autenticação JWT;
- perfis de acesso;
- validações do Safe Change Engine;
- persistência relacional com SQLAlchemy 2.0;
- logs de auditoria;
- análise opcional por IA generativa.

## Principais funcionalidades

- Login com JWT.
- Perfis `admin`, `operator` e `viewer`.
- Cadastro e consulta de alunos.
- CPF com máscara `000.000.000-00` e validação de exatamente 11 dígitos.
- Cadastro e consulta de cursos.
- Criação e controle de matrículas.
- Bloqueio de alterações perigosas por regra de negócio.
- Solicitações administrativas com fluxo de revisão.
- Análise de solicitações com OpenAI API ou fallback local.
- Auditoria para alterações críticas.
- Frontend React em Português BR.
- Docker Compose com PostgreSQL, API e frontend.
- Testes automatizados com Pytest.

## Onde Python está presente

Python é o centro do projeto:

- API FastAPI em `app/main.py`;
- rotas REST em `app/api/routes`;
- autenticação e segurança em `app/core`;
- modelos SQLAlchemy 2.0 em `app/models`;
- schemas Pydantic v2 em `app/schemas`;
- regras de negócio em `app/services`;
- Safe Change Engine em `app/services/safe_change_service.py`;
- auditoria em `app/services/audit_service.py`;
- integração com IA em `app/services/ai_service.py`;
- seed do banco em `app/db/seed.py`;
- testes em `app/tests`.

O React consome essa API Python e apresenta a experiência visual do produto.

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

### Infraestrutura

- Docker
- Docker Compose
- PostgreSQL containerizado

## Arquitetura

```text
eduflow-ai/
├── app/
│   ├── api/routes/                  # Endpoints REST
│   ├── core/                        # Configuração, segurança e permissões
│   ├── db/                          # Conexão, metadata e seed
│   ├── models/                      # Modelos SQLAlchemy
│   ├── repositories/                # Acesso a dados
│   ├── schemas/                     # Contratos Pydantic
│   ├── services/                    # Regras de negócio, IA e auditoria
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

- `users`: usuários internos e perfis.
- `students`: alunos e status acadêmico.
- `courses`: cursos.
- `enrollments`: matrículas e status financeiro.
- `administrative_requests`: solicitações administrativas.
- `ai_request_analysis`: análises geradas por IA.
- `audit_logs`: trilha de auditoria.

## Regras de negócio

- Admin pode gerenciar usuários e consultar auditoria.
- Operator pode criar e alterar dados operacionais.
- Viewer pode apenas consultar.
- Aluno bloqueado não pode receber matrícula.
- Curso inativo não aceita matrícula.
- Matrícula não pode ser ativada com pagamento vencido.
- Matrícula concluída não pode ser cancelada.
- CPF deve conter exatamente 11 dígitos reais.
- E-mail e CPF duplicados retornam erro claro.

## Safe Change Engine

O Safe Change Engine centraliza regras que evitam alterações perigosas no banco. Ele representa o diferencial do projeto: trocar updates manuais por validações aplicacionais rastreáveis.

Arquivo principal:

```text
app/services/safe_change_service.py
```

Funções principais:

- `validate_student_status_change`
- `validate_enrollment_creation`
- `validate_enrollment_status_change`
- `validate_payment_status_change`
- `validate_request_status_transition`

## Auditoria

Alterações críticas geram registros em `audit_logs`, incluindo:

- usuário;
- ação;
- entidade;
- registro afetado;
- valor antigo;
- novo valor;
- motivo;
- data.

Exemplos de ações auditadas:

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

O endpoint abaixo analisa uma solicitação administrativa:

```http
POST /requests/{request_id}/ai-analysis
```

Retorno esperado:

```json
{
  "predicted_category": "financial_review",
  "priority": "high",
  "summary": "Aluno solicita revisão de cobrança possivelmente indevida.",
  "suggested_action": "Encaminhar para análise financeira.",
  "risk_level": "medium",
  "model_used": "gpt-4o-mini"
}
```

Se `OPENAI_API_KEY` não estiver configurada, o sistema usa fallback local para não quebrar o ambiente de desenvolvimento.

## Como rodar com Docker

```bash
docker compose up --build
```

Serviços:

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

## Variáveis de ambiente

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

Essas credenciais são apenas para ambiente local.

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

Última validação local:

```text
12 passed
```

## Frontend

O frontend React foi criado para ser a experiência principal do produto. Ele inclui:

- tela de login;
- painel com métricas;
- cadastros de alunos, cursos, matrículas e solicitações;
- máscara e validação de CPF;
- área de análise com IA;
- auditoria para usuários admin;
- interface em Português BR;
- visual leve, colorido e profissional.

## Roadmap

- RAG com políticas acadêmicas.
- Integração com n8n.
- Notificações automáticas.
- Relatórios em PDF.
- Deploy em cloud.
- Testes de carga.
- CI/CD.
- Suíte de testes frontend.

## O que este projeto demonstra

- Arquitetura backend Python limpa.
- Separação entre rotas, serviços, schemas, modelos e repositórios.
- Regras de negócio fora das rotas.
- Validação de dados com Pydantic.
- Persistência relacional com SQLAlchemy 2.0.
- Uso prático de IA generativa.
- Frontend consumindo uma API real.
- Dockerização de uma aplicação full stack.
