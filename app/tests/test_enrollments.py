from fastapi.testclient import TestClient


def _create_student(client: TestClient, headers: dict[str, str], status: str = "active") -> int:
    response = client.post(
        "/students",
        headers=headers,
        json={
            "name": f"Student {status}",
            "email": f"{status}.student@example.com",
            "cpf": f"9998887776{len(status)}",
            "status": status,
        },
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def _create_course(client: TestClient, headers: dict[str, str]) -> int:
    response = client.post(
        "/courses",
        headers=headers,
        json={"name": "Backend Python", "category": "Technology", "workload_hours": 100},
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def test_prevents_enrollment_for_blocked_student(
    client: TestClient,
    operator_headers: dict[str, str],
) -> None:
    student_id = _create_student(client, operator_headers, status="blocked")
    course_id = _create_course(client, operator_headers)
    response = client.post(
        "/enrollments",
        headers=operator_headers,
        json={"student_id": student_id, "course_id": course_id},
    )
    assert response.status_code == 400
    assert "blocked student" in response.json()["detail"]


def test_prevents_activation_with_overdue_payment(
    client: TestClient,
    operator_headers: dict[str, str],
) -> None:
    student_id = _create_student(client, operator_headers)
    course_id = _create_course(client, operator_headers)
    enrollment_response = client.post(
        "/enrollments",
        headers=operator_headers,
        json={
            "student_id": student_id,
            "course_id": course_id,
            "payment_status": "overdue",
        },
    )
    assert enrollment_response.status_code == 201
    enrollment_id = enrollment_response.json()["id"]
    response = client.patch(
        f"/enrollments/{enrollment_id}/status",
        headers=operator_headers,
        json={"status": "active"},
    )
    assert response.status_code == 400
    assert "overdue payment" in response.json()["detail"]


def test_admin_can_consult_audit_logs(client: TestClient, admin_headers: dict[str, str]) -> None:
    student_id = _create_student(client, admin_headers)
    course_id = _create_course(client, admin_headers)
    client.post(
        "/enrollments",
        headers=admin_headers,
        json={"student_id": student_id, "course_id": course_id},
    )
    response = client.get("/audit-logs", headers=admin_headers)
    assert response.status_code == 200
    assert any(log["action"] == "enrollment_created" for log in response.json())
