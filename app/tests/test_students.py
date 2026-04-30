from fastapi.testclient import TestClient

from app.models.student import Student


def test_operator_can_create_student(client: TestClient, operator_headers: dict[str, str]) -> None:
    response = client.post(
        "/students",
        headers=operator_headers,
        json={"name": "Ana Silva", "email": "ana@example.com", "cpf": "12345678901"},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "active"
    assert response.json()["cpf"] == "123.456.789-01"


def test_student_cpf_must_have_exactly_11_digits(
    client: TestClient,
    operator_headers: dict[str, str],
) -> None:
    response = client.post(
        "/students",
        headers=operator_headers,
        json={"name": "CPF Inválido", "email": "cpf.invalido@example.com", "cpf": "1234567890"},
    )
    assert response.status_code == 422


def test_student_duplicate_email_returns_clear_conflict(
    client: TestClient,
    operator_headers: dict[str, str],
) -> None:
    payload = {"name": "Ana Silva", "email": "ana.duplicada@example.com", "cpf": "98765432100"}
    first_response = client.post("/students", headers=operator_headers, json=payload)
    second_response = client.post(
        "/students",
        headers=operator_headers,
        json={**payload, "cpf": "98765432101"},
    )
    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Já existe um aluno cadastrado com este e-mail."


def test_student_duplicate_cpf_returns_clear_conflict(
    client: TestClient,
    operator_headers: dict[str, str],
) -> None:
    payload = {"name": "João CPF", "email": "joao.cpf@example.com", "cpf": "11122233344"}
    first_response = client.post("/students", headers=operator_headers, json=payload)
    second_response = client.post(
        "/students",
        headers=operator_headers,
        json={**payload, "email": "joao.cpf.2@example.com"},
    )
    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Já existe um aluno cadastrado com este CPF."


def test_students_list_does_not_break_with_legacy_invalid_cpf(
    client: TestClient,
    operator_headers: dict[str, str],
) -> None:
    from app.tests.conftest import TestingSessionLocal

    with TestingSessionLocal() as db:
        db.add(
            Student(
                name="Aluno Legado",
                email="legado@example.com",
                cpf="1234567891011",
                status="active",
            )
        )
        db.commit()

    response = client.get("/students", headers=operator_headers)

    assert response.status_code == 200
    assert any(student["cpf"] == "1234567891011" for student in response.json())
