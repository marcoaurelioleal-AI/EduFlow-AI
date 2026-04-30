import os
from collections import Counter
from typing import Any

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(page_title="EduFlow AI Admin", layout="wide")


def api_request(method: str, path: str, token: str | None = None, **kwargs: Any) -> requests.Response:
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.request(method, f"{API_URL}{path}", headers=headers, timeout=20, **kwargs)


def login(email: str, password: str) -> None:
    response = api_request("POST", "/auth/login", json={"email": email, "password": password})
    if response.status_code == 200:
        st.session_state.token = response.json()["access_token"]
        me = api_request("GET", "/users/me", token=st.session_state.token)
        st.session_state.user = me.json() if me.status_code == 200 else {}
        st.success("Login realizado com sucesso.")
    else:
        st.error("Credenciais inválidas ou API indisponível.")


def require_login() -> bool:
    if "token" not in st.session_state:
        st.info("Faça login na sidebar para acessar o painel.")
        return False
    return True


def fetch_json(path: str) -> list[dict[str, Any]]:
    response = api_request("GET", path, token=st.session_state.token)
    if response.status_code != 200:
        st.warning(f"Não foi possível carregar {path}: {response.text}")
        return []
    data = response.json()
    return data if isinstance(data, list) else [data]


with st.sidebar:
    st.title("EduFlow AI")
    st.caption(f"API: {API_URL}")
    if "token" not in st.session_state:
        with st.form("login_form"):
            email = st.text_input("E-mail", value="admin@eduflow.ai")
            password = st.text_input("Senha", value="admin123", type="password")
            submitted = st.form_submit_button("Entrar")
        if submitted:
            login(email, password)
    else:
        user = st.session_state.get("user", {})
        st.success(f"{user.get('name', 'Usuário')} ({user.get('role', '-')})")
        if st.button("Sair"):
            st.session_state.clear()
            st.rerun()

    page = st.radio(
        "Navegação",
        ["Dashboard", "Students", "Enrollments", "Requests", "AI Analysis", "Audit Logs"],
    )

st.title("EduFlow AI Administrative Dashboard")

if require_login():
    students = fetch_json("/students")
    enrollments = fetch_json("/enrollments")
    requests_data = fetch_json("/requests")
    user_role = st.session_state.get("user", {}).get("role")

    if page == "Dashboard":
        pending_requests = [item for item in requests_data if item.get("status") == "pending"]
        priority_counter = Counter(item.get("priority") or "not_set" for item in requests_data)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de alunos", len(students))
        col2.metric("Total de matrículas", len(enrollments))
        col3.metric("Solicitações pendentes", len(pending_requests))
        col4.metric("Prioridades mapeadas", len(priority_counter))
        st.subheader("Solicitações por prioridade")
        st.bar_chart(priority_counter)

    elif page == "Students":
        st.subheader("Students")
        st.dataframe(students, use_container_width=True)

    elif page == "Enrollments":
        st.subheader("Enrollments")
        st.dataframe(enrollments, use_container_width=True)

    elif page == "Requests":
        st.subheader("Administrative Requests")
        st.dataframe(requests_data, use_container_width=True)
        with st.expander("Detalhes técnicos"):
            st.json(requests_data[:5])

    elif page == "AI Analysis":
        st.subheader("AI Analysis")
        request_ids = [item["id"] for item in requests_data]
        if request_ids:
            request_id = st.selectbox("Solicitação", request_ids)
            if st.button("Solicitar análise com IA"):
                response = api_request(
                    "POST",
                    f"/requests/{request_id}/ai-analysis",
                    token=st.session_state.token,
                )
                if response.status_code == 201:
                    st.success("Análise gerada e salva.")
                    st.json(response.json())
                else:
                    st.error(response.text)
        else:
            st.info("Nenhuma solicitação cadastrada.")

    elif page == "Audit Logs":
        st.subheader("Audit Logs")
        if user_role != "admin":
            st.warning("Apenas usuários admin podem consultar logs de auditoria.")
        else:
            logs = fetch_json("/audit-logs")
            st.dataframe(logs[:50], use_container_width=True)
