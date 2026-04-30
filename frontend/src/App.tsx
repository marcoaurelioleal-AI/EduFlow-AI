import {
  Activity,
  BrainCircuit,
  ClipboardList,
  GraduationCap,
  LayoutDashboard,
  LibraryBig,
  Lock,
  LogOut,
  Plus,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  UserRound,
  UsersRound,
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type Page = "painel" | "alunos" | "cursos" | "matriculas" | "solicitacoes" | "ia" | "auditoria";

type User = {
  id: number;
  name: string;
  email: string;
  role: "admin" | "operator" | "viewer";
  is_active: boolean;
};

type Student = {
  id: number;
  name: string;
  email: string;
  cpf: string;
  status: string;
};

type Course = {
  id: number;
  name: string;
  category: string;
  workload_hours: number;
  is_active: boolean;
};

type Enrollment = {
  id: number;
  student_id: number;
  course_id: number;
  status: string;
  payment_status: string;
};

type AdministrativeRequest = {
  id: number;
  student_id: number;
  request_type: string;
  description: string;
  status: string;
  priority: string | null;
};

type AuditLog = {
  id: number;
  user_id: number | null;
  action: string;
  entity_type: string;
  entity_id: number;
  created_at: string;
};

type AIAnalysis = {
  id: number;
  request_id: number;
  predicted_category: string;
  priority: string;
  summary: string;
  suggested_action: string;
  risk_level: string;
  model_used: string;
};

type ApiState = {
  students: Student[];
  courses: Course[];
  enrollments: Enrollment[];
  requests: AdministrativeRequest[];
  auditLogs: AuditLog[];
};

const pageItems: Array<{ key: Page; label: string; icon: typeof LayoutDashboard }> = [
  { key: "painel", label: "Painel", icon: LayoutDashboard },
  { key: "alunos", label: "Alunos", icon: UsersRound },
  { key: "cursos", label: "Cursos", icon: LibraryBig },
  { key: "matriculas", label: "Matrículas", icon: GraduationCap },
  { key: "solicitacoes", label: "Solicitações", icon: ClipboardList },
  { key: "ia", label: "Análise com IA", icon: BrainCircuit },
  { key: "auditoria", label: "Auditoria", icon: ShieldCheck },
];

const labels: Record<string, string> = {
  admin: "Administrador",
  operator: "Operador",
  viewer: "Leitor",
  active: "Ativo",
  inactive: "Inativo",
  blocked: "Bloqueado",
  graduated: "Formado",
  pending: "Pendente",
  paid: "Pago",
  overdue: "Vencido",
  refunded: "Reembolsado",
  cancelled: "Cancelado",
  completed: "Concluído",
  in_review: "Em revisão",
  approved: "Aprovado",
  rejected: "Rejeitado",
  low: "Baixa",
  medium: "Média",
  high: "Alta",
  critical: "Crítica",
  enrollment_change: "Alteração de matrícula",
  discount_request: "Pedido de desconto",
  refund_request: "Pedido de reembolso",
  document_request: "Documento acadêmico",
  financial_review: "Revisão financeira",
  cancellation_request: "Cancelamento",
};

const initialState: ApiState = {
  students: [],
  courses: [],
  enrollments: [],
  requests: [],
  auditLogs: [],
};

function translate(value: string | null | undefined) {
  if (!value) return "Não definido";
  return labels[value] ?? value;
}

function onlyDigits(value: string) {
  return value.replace(/\D/g, "");
}

function formatCPF(value: string) {
  const digits = onlyDigits(value).slice(0, 11);
  return digits
    .replace(/^(\d{3})(\d)/, "$1.$2")
    .replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3")
    .replace(/^(\d{3})\.(\d{3})\.(\d{3})(\d)/, "$1.$2.$3-$4");
}

function badgeTone(value: string | null | undefined) {
  if (value === "critical" || value === "blocked" || value === "overdue" || value === "rejected") {
    return "danger";
  }
  if (value === "high" || value === "pending" || value === "in_review") return "warning";
  if (value === "active" || value === "paid" || value === "approved" || value === "completed") {
    return "success";
  }
  return "soft";
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("eduflow_token") ?? "");
  const [user, setUser] = useState<User | null>(null);
  const [page, setPage] = useState<Page>("painel");
  const [state, setState] = useState<ApiState>(initialState);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null);

  const isAdmin = user?.role === "admin";
  const canOperate = user?.role === "admin" || user?.role === "operator";

  async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const data = await response.json().catch(() => null);
      throw new Error(data?.detail ?? "Não foi possível concluir a operação.");
    }

    return response.json() as Promise<T>;
  }

  async function loadData() {
    if (!token) return;
    setLoading(true);
    setMessage("");
    try {
      const me = await request<User>("/users/me");
      setUser(me);
      const [students, courses, enrollments, requests] = await Promise.all([
        request<Student[]>("/students"),
        request<Course[]>("/courses"),
        request<Enrollment[]>("/enrollments"),
        request<AdministrativeRequest[]>("/requests"),
      ]);
      let auditLogs: AuditLog[] = [];
      if (me.role === "admin") {
        auditLogs = await request<AuditLog[]>("/audit-logs");
      }
      setState({ students, courses, enrollments, requests, auditLogs });
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Erro inesperado ao carregar dados.");
    } finally {
      setLoading(false);
    }
  }

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    setLoading(true);
    try {
      const data = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.get("email"),
          password: formData.get("password"),
        }),
      }).then((response) => {
        if (!response.ok) throw new Error("E-mail ou senha inválidos.");
        return response.json();
      });
      localStorage.setItem("eduflow_token", data.access_token);
      setToken(data.access_token);
      setMessage("Login realizado com sucesso.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Erro ao fazer login.");
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    localStorage.removeItem("eduflow_token");
    setToken("");
    setUser(null);
    setState(initialState);
  }

  async function submitJson(path: string, data: Record<string, unknown>) {
    setLoading(true);
    setMessage("");
    try {
      await request(path, { method: "POST", body: JSON.stringify(data) });
      setMessage("Registro criado com sucesso.");
      await loadData();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Erro ao salvar registro.");
    } finally {
      setLoading(false);
    }
  }

  async function runAIAnalysis(requestId: number) {
    setLoading(true);
    setMessage("");
    try {
      const result = await request<AIAnalysis>(`/requests/${requestId}/ai-analysis`, { method: "POST" });
      setAnalysis(result);
      setMessage("Análise com IA gerada e salva no banco.");
      await loadData();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Erro ao gerar análise com IA.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (token) void loadData();
  }, [token]);

  const pendingRequests = state.requests.filter((item) => item.status === "pending").length;
  const activeStudents = state.students.filter((item) => item.status === "active").length;
  const overdueEnrollments = state.enrollments.filter((item) => item.payment_status === "overdue").length;
  const prioritySummary = useMemo(() => {
    return state.requests.reduce<Record<string, number>>((acc, item) => {
      const key = item.priority ?? "not_set";
      acc[key] = (acc[key] ?? 0) + 1;
      return acc;
    }, {});
  }, [state.requests]);

  if (!token) {
    return (
      <main className="login-page">
        <section className="login-hero">
          <div className="brand-mark">
            <Sparkles size={24} />
          </div>
          <p className="eyebrow">Backoffice acadêmico inteligente</p>
          <h1>EduFlow AI</h1>
          <p>
            Plataforma para automatizar processos acadêmicos críticos com segurança,
            rastreabilidade e apoio de IA, reduzindo alterações manuais no banco e
            dando mais controle às equipes administrativas.
          </p>
          <div className="hero-pills">
            <span>FastAPI</span>
            <span>PostgreSQL</span>
            <span>IA</span>
            <span>Auditoria</span>
          </div>
        </section>

        <section className="login-panel">
          <div>
            <p className="eyebrow">Acesso local</p>
            <h2>Entrar no painel</h2>
            <p className="muted">Use as credenciais criadas pelo seed para explorar o sistema.</p>
          </div>
          <form onSubmit={handleLogin}>
            <label>
              E-mail
              <input name="email" type="email" defaultValue="admin@eduflow.ai" required />
            </label>
            <label>
              Senha
              <input name="password" type="password" defaultValue="admin123" required />
            </label>
            <button className="primary-button" type="submit" disabled={loading}>
              <Lock size={18} />
              {loading ? "Entrando..." : "Entrar"}
            </button>
          </form>
          {message && <p className="feedback">{message}</p>}
        </section>
      </main>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="logo-row">
          <div className="logo-icon">
            <Sparkles size={22} />
          </div>
          <div>
            <strong>EduFlow AI</strong>
            <span>Operações acadêmicas</span>
          </div>
        </div>
        <nav>
          {pageItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                className={page === item.key ? "nav-button active" : "nav-button"}
                key={item.key}
                onClick={() => setPage(item.key)}
                type="button"
              >
                <Icon size={18} />
                {item.label}
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Painel administrativo</p>
            <h1>{pageItems.find((item) => item.key === page)?.label}</h1>
          </div>
          <div className="topbar-actions">
            <button className="icon-button" onClick={loadData} title="Atualizar dados" type="button">
              <RefreshCw size={18} />
            </button>
            <div className="user-chip">
              <UserRound size={18} />
              <span>{user?.name}</span>
              <strong>{translate(user?.role)}</strong>
            </div>
            <button className="icon-button" onClick={logout} title="Sair" type="button">
              <LogOut size={18} />
            </button>
          </div>
        </header>

        {message && <div className="notice">{message}</div>}

        {page === "painel" && (
          <section className="page-grid">
            <Metric icon={UsersRound} label="Alunos ativos" value={activeStudents} tone="mint" />
            <Metric icon={GraduationCap} label="Matrículas" value={state.enrollments.length} tone="sky" />
            <Metric icon={ClipboardList} label="Solicitações pendentes" value={pendingRequests} tone="sun" />
            <Metric icon={Activity} label="Pagamentos vencidos" value={overdueEnrollments} tone="coral" />

            <section className="wide-section">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">Triagem</p>
                  <h2>Solicitações por prioridade</h2>
                </div>
              </div>
              <div className="priority-bars">
                {["critical", "high", "medium", "low", "not_set"].map((key) => (
                  <div className="priority-row" key={key}>
                    <span>{key === "not_set" ? "Não definida" : translate(key)}</span>
                    <div>
                      <i style={{ width: `${Math.max((prioritySummary[key] ?? 0) * 18, 8)}%` }} />
                    </div>
                    <strong>{prioritySummary[key] ?? 0}</strong>
                  </div>
                ))}
              </div>
            </section>
          </section>
        )}

        {page === "alunos" && (
          <DataSection
            title="Alunos"
            subtitle="Cadastro e situação acadêmica."
            action={
              canOperate && (
                <QuickStudentForm onSubmit={(data) => submitJson("/students", data)} disabled={loading} />
              )
            }
          >
            <DataTable
              columns={["ID", "Nome", "E-mail", "CPF", "Status"]}
              rows={state.students.map((item) => [
                item.id,
                item.name,
                item.email,
                formatCPF(item.cpf),
                <Badge key={item.id} value={item.status} />,
              ])}
            />
          </DataSection>
        )}

        {page === "cursos" && (
          <DataSection
            title="Cursos"
            subtitle="Catálogo acadêmico disponível para matrícula."
            action={canOperate && <QuickCourseForm onSubmit={(data) => submitJson("/courses", data)} disabled={loading} />}
          >
            <DataTable
              columns={["ID", "Curso", "Categoria", "Carga horária", "Situação"]}
              rows={state.courses.map((item) => [
                item.id,
                item.name,
                item.category,
                `${item.workload_hours}h`,
                <Badge key={item.id} value={item.is_active ? "active" : "inactive"} />,
              ])}
            />
          </DataSection>
        )}

        {page === "matriculas" && (
          <DataSection
            title="Matrículas"
            subtitle="Fluxo acadêmico e financeiro protegido por regras."
            action={
              canOperate && (
                <QuickEnrollmentForm
                  students={state.students}
                  courses={state.courses}
                  onSubmit={(data) => submitJson("/enrollments", data)}
                  disabled={loading}
                />
              )
            }
          >
            <DataTable
              columns={["ID", "Aluno", "Curso", "Status", "Pagamento"]}
              rows={state.enrollments.map((item) => [
                item.id,
                studentName(state.students, item.student_id),
                courseName(state.courses, item.course_id),
                <Badge key={`${item.id}-status`} value={item.status} />,
                <Badge key={`${item.id}-payment`} value={item.payment_status} />,
              ])}
            />
          </DataSection>
        )}

        {page === "solicitacoes" && (
          <DataSection
            title="Solicitações administrativas"
            subtitle="Pedidos internos com prioridade, status e rastreabilidade."
            action={
              canOperate && (
                <QuickRequestForm
                  students={state.students}
                  onSubmit={(data) => submitJson("/requests", data)}
                  disabled={loading}
                />
              )
            }
          >
            <DataTable
              columns={["ID", "Aluno", "Tipo", "Status", "Prioridade", "Descrição"]}
              rows={state.requests.map((item) => [
                item.id,
                studentName(state.students, item.student_id),
                translate(item.request_type),
                <Badge key={`${item.id}-status`} value={item.status} />,
                <Badge key={`${item.id}-priority`} value={item.priority} />,
                item.description,
              ])}
            />
          </DataSection>
        )}

        {page === "ia" && (
          <DataSection title="Análise com IA" subtitle="Triagem automática usando o serviço Python de IA.">
            <div className="analysis-grid">
              {state.requests.map((item) => (
                <article className="request-item" key={item.id}>
                  <div>
                    <strong>#{item.id} - {translate(item.request_type)}</strong>
                    <p>{item.description}</p>
                    <Badge value={item.priority} />
                  </div>
                  <button
                    className="secondary-button"
                    disabled={!canOperate || loading}
                    onClick={() => runAIAnalysis(item.id)}
                    type="button"
                  >
                    <BrainCircuit size={17} />
                    Analisar
                  </button>
                </article>
              ))}
            </div>
            {analysis && (
              <section className="ai-result">
                <p className="eyebrow">Resultado salvo</p>
                <h2>{analysis.summary}</h2>
                <p>{analysis.suggested_action}</p>
                <div className="hero-pills">
                  <span>Prioridade: {translate(analysis.priority)}</span>
                  <span>Risco: {translate(analysis.risk_level)}</span>
                  <span>Modelo: {analysis.model_used}</span>
                </div>
              </section>
            )}
          </DataSection>
        )}

        {page === "auditoria" && (
          <DataSection title="Auditoria" subtitle="Histórico de alterações críticas do sistema.">
            {!isAdmin ? (
              <div className="empty-state">Apenas administradores podem consultar os logs de auditoria.</div>
            ) : (
              <DataTable
                columns={["ID", "Ação", "Entidade", "Registro", "Usuário", "Data"]}
                rows={state.auditLogs.map((item) => [
                  item.id,
                  item.action,
                  item.entity_type,
                  item.entity_id,
                  item.user_id ?? "Sistema",
                  new Date(item.created_at).toLocaleString("pt-BR"),
                ])}
              />
            )}
          </DataSection>
        )}
      </main>
    </div>
  );
}

function Metric({
  icon: Icon,
  label,
  value,
  tone,
}: {
  icon: typeof UsersRound;
  label: string;
  value: number;
  tone: string;
}) {
  return (
    <article className={`metric metric-${tone}`}>
      <Icon size={24} />
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function DataSection({
  title,
  subtitle,
  action,
  children,
}: {
  title: string;
  subtitle: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="data-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">EduFlow AI</p>
          <h2>{title}</h2>
          <p className="muted">{subtitle}</p>
        </div>
      </div>
      {action}
      {children}
    </section>
  );
}

function DataTable({ columns, rows }: { columns: string[]; rows: Array<Array<ReactNode>> }) {
  if (rows.length === 0) return <div className="empty-state">Nenhum registro encontrado.</div>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index}>
              {row.map((cell, cellIndex) => (
                <td key={cellIndex}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Badge({ value }: { value: string | null | undefined }) {
  return <span className={`badge badge-${badgeTone(value)}`}>{translate(value)}</span>;
}

function QuickStudentForm({
  onSubmit,
  disabled,
}: {
  onSubmit: (data: Record<string, unknown>) => void;
  disabled: boolean;
}) {
  return (
    <InlineForm
      disabled={disabled}
      fields={[
        { name: "name", label: "Nome", placeholder: "Marina Costa" },
        { name: "email", label: "E-mail", placeholder: "marina@email.com", type: "email" },
        {
          name: "cpf",
          label: "CPF",
          placeholder: "000.000.000-00",
          inputMode: "numeric",
          maxLength: 14,
          pattern: "\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}",
          title: "Digite exatamente 11 números. O campo será formatado como 000.000.000-00.",
          mask: "cpf",
        },
      ]}
      onSubmit={onSubmit}
    />
  );
}

function QuickCourseForm({
  onSubmit,
  disabled,
}: {
  onSubmit: (data: Record<string, unknown>) => void;
  disabled: boolean;
}) {
  return (
    <InlineForm
      disabled={disabled}
      fields={[
        { name: "name", label: "Curso", placeholder: "Python para Back-end" },
        { name: "category", label: "Categoria", placeholder: "Tecnologia" },
        { name: "workload_hours", label: "Horas", placeholder: "120", type: "number" },
      ]}
      onSubmit={(data) => onSubmit({ ...data, workload_hours: Number(data.workload_hours) })}
    />
  );
}

function QuickEnrollmentForm({
  students,
  courses,
  onSubmit,
  disabled,
}: {
  students: Student[];
  courses: Course[];
  onSubmit: (data: Record<string, unknown>) => void;
  disabled: boolean;
}) {
  return (
    <form
      className="inline-form"
      onSubmit={(event) => {
        event.preventDefault();
        const data = new FormData(event.currentTarget);
        onSubmit({
          student_id: Number(data.get("student_id")),
          course_id: Number(data.get("course_id")),
        });
        event.currentTarget.reset();
      }}
    >
      <SelectField label="Aluno" name="student_id" options={students.map((item) => [item.id, item.name])} />
      <SelectField label="Curso" name="course_id" options={courses.map((item) => [item.id, item.name])} />
      <button className="primary-button compact" disabled={disabled} type="submit">
        <Plus size={16} />
        Criar
      </button>
    </form>
  );
}

function QuickRequestForm({
  students,
  onSubmit,
  disabled,
}: {
  students: Student[];
  onSubmit: (data: Record<string, unknown>) => void;
  disabled: boolean;
}) {
  return (
    <form
      className="inline-form request-form"
      onSubmit={(event) => {
        event.preventDefault();
        const data = new FormData(event.currentTarget);
        onSubmit({
          student_id: Number(data.get("student_id")),
          request_type: data.get("request_type"),
          description: data.get("description"),
        });
        event.currentTarget.reset();
      }}
    >
      <SelectField label="Aluno" name="student_id" options={students.map((item) => [item.id, item.name])} />
      <label>
        Tipo
        <select name="request_type" required>
          <option value="financial_review">Revisão financeira</option>
          <option value="enrollment_change">Alteração de matrícula</option>
          <option value="discount_request">Pedido de desconto</option>
          <option value="refund_request">Pedido de reembolso</option>
          <option value="document_request">Documento acadêmico</option>
          <option value="cancellation_request">Cancelamento</option>
        </select>
      </label>
      <label className="grow-field">
        Descrição
        <input name="description" placeholder="Aluno solicita revisão de cobrança..." required />
      </label>
      <button className="primary-button compact" disabled={disabled} type="submit">
        <Plus size={16} />
        Criar
      </button>
    </form>
  );
}

function InlineForm({
  fields,
  onSubmit,
  disabled,
}: {
  fields: Array<{
    name: string;
    label: string;
    placeholder: string;
    type?: string;
    inputMode?: "numeric";
    maxLength?: number;
    pattern?: string;
    title?: string;
    mask?: "cpf";
  }>;
  onSubmit: (data: Record<string, unknown>) => void;
  disabled: boolean;
}) {
  return (
    <form
      className="inline-form"
      onSubmit={(event) => {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        const payload = Object.fromEntries(formData.entries());
        onSubmit(payload);
        event.currentTarget.reset();
      }}
    >
      {fields.map((field) => (
        <label key={field.name}>
          {field.label}
          <input
            inputMode={field.inputMode}
            maxLength={field.maxLength}
            name={field.name}
            onChange={(event) => {
              if (field.mask === "cpf") {
                event.currentTarget.value = formatCPF(event.currentTarget.value);
              }
            }}
            pattern={field.pattern}
            placeholder={field.placeholder}
            title={field.title}
            type={field.type ?? "text"}
            required
          />
        </label>
      ))}
      <button className="primary-button compact" disabled={disabled} type="submit">
        <Plus size={16} />
        Criar
      </button>
    </form>
  );
}

function SelectField({
  label,
  name,
  options,
}: {
  label: string;
  name: string;
  options: Array<[number, string]>;
}) {
  return (
    <label>
      {label}
      <select name={name} required>
        <option value="">Selecione</option>
        {options.map(([value, text]) => (
          <option key={value} value={value}>
            {text}
          </option>
        ))}
      </select>
    </label>
  );
}

function studentName(students: Student[], id: number) {
  return students.find((student) => student.id === id)?.name ?? `Aluno #${id}`;
}

function courseName(courses: Course[], id: number) {
  return courses.find((course) => course.id === id)?.name ?? `Curso #${id}`;
}

export default App;
