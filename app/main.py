from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    administrative_requests,
    ai_analysis,
    audit_logs,
    auth,
    courses,
    enrollments,
    health,
    students,
    users,
)

app = FastAPI(
    title="EduFlow AI",
    description="API para automação de operações acadêmicas com auditoria, controle de acesso e triagem assistida por IA.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8502",
        "http://127.0.0.1:8502",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(students.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(administrative_requests.router)
app.include_router(ai_analysis.router)
app.include_router(audit_logs.router)
