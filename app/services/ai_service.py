import json
from typing import Any

from openai import OpenAI

from app.core.config import settings

ALLOWED_PRIORITIES = {"low", "medium", "high", "critical"}
ALLOWED_RISKS = {"low", "medium", "high"}


def _fallback_analysis(description: str, request_type: str | None) -> dict[str, str]:
    lowered = description.lower()
    priority = "medium"
    risk_level = "low"
    if any(word in lowered for word in ["urgente", "bloqueio", "cobrança", "indevida", "cancelamento"]):
        priority = "high"
        risk_level = "medium"
    return {
        "predicted_category": request_type or "financial_review",
        "priority": priority,
        "summary": "Análise local gerada porque a OpenAI API não está configurada ou falhou.",
        "suggested_action": "Revisar a solicitação por um operador e validar os dados antes da alteração.",
        "risk_level": risk_level,
    }


def _normalize_analysis(data: dict[str, Any], request_type: str | None) -> dict[str, str]:
    priority = data.get("priority") if data.get("priority") in ALLOWED_PRIORITIES else "medium"
    risk_level = data.get("risk_level") if data.get("risk_level") in ALLOWED_RISKS else "low"
    return {
        "predicted_category": str(data.get("predicted_category") or request_type or "financial_review"),
        "priority": priority,
        "summary": str(data.get("summary") or "Resumo não informado pela IA."),
        "suggested_action": str(data.get("suggested_action") or "Encaminhar para revisão administrativa."),
        "risk_level": risk_level,
    }


def analyze_administrative_request(description: str, request_type: str | None = None) -> dict[str, str]:
    """Analyze an academic backoffice request with OpenAI, using a local fallback in development."""
    if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
        return _fallback_analysis(description, request_type)

    prompt = (
        "Você é um assistente de triagem administrativa acadêmica. "
        "Baseie-se apenas na descrição fornecida, não invente dados do aluno e retorne JSON com: "
        "predicted_category, priority, summary, suggested_action, risk_level. "
        "priority deve ser low, medium, high ou critical. risk_level deve ser low, medium ou high."
    )
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": json.dumps(
                        {"description": description, "request_type": request_type},
                        ensure_ascii=False,
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        return _normalize_analysis(json.loads(content), request_type)
    except Exception:
        return _fallback_analysis(description, request_type)
