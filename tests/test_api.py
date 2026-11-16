import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.validation import MAX_CSV_BYTES


@pytest.fixture
def setup(tmp_path):
    db_path = tmp_path / "data" / "schemaguard.db"
    return TestClient(create_app(db_path)), db_path


def add_contract(client, **changes):
    payload = {"name": "orders", "required_columns": ["id", "amount"], "missing_value_threshold": 25}
    payload.update(changes)
    return client.post("/api/contracts", json=payload)


def upload(client, data, contract_id=1, filename="orders.csv"):
    return client.post("/api/validate", data={"contract_id": contract_id}, files={"file": (filename, data, "text/csv")})


def test_contract_validation_history_and_restart(setup):
    client, db_path = setup
    assert client.get("/api/health").json() == {"status": "ok"}
    created = add_contract(client)
    assert created.status_code == 201
    assert created.json()["required_columns"] == ["id", "amount"]
    assert add_contract(client).status_code == 409
    assert len(client.get("/api/contracts").json()) == 1

    passed = upload(client, b"id,amount\n1,20\n2,30\n")
    assert passed.status_code == 201
    assert passed.json()["status"] == "PASS"
    assert passed.json()["reasons"] == []
    failed = upload(client, b"id,other\n ,x\n", filename="failed.csv")
    assert failed.status_code == 201
    assert failed.json()["status"] == "FAIL"
    assert len(failed.json()["reasons"]) == 2

    restarted = TestClient(create_app(db_path))
    assert len(restarted.get("/api/contracts").json()) == 1
    history = restarted.get("/api/validations").json()
    assert [item["status"] for item in history] == ["FAIL", "PASS"]
    assert history[0]["filename"] == "failed.csv"
    assert history[0]["contract_id"] == created.json()["id"]
    assert history[0]["created_at"]
    with sqlite3.connect(db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM validations").fetchone()[0] == 2


@pytest.mark.parametrize("changes", [
    {"name": " "}, {"required_columns": []},
    {"required_columns": ["id", "id"]}, {"required_columns": ["id", " "]},
    {"missing_value_threshold": -1}, {"missing_value_threshold": 101},
    {"missing_value_threshold": "nan"},
])
def test_rejects_invalid_contracts(setup, changes):
    client, _ = setup
    assert add_contract(client, **changes).status_code == 422
    assert client.get("/api/contracts").json() == []


@pytest.mark.parametrize("data, status", [
    (b"", 400), (b"\xff", 400), (b"a,b\n1\n", 400),
    (b'a,b\n"bad,2\n', 400), (b"id,amount\n1,2\n" + b"x" * MAX_CSV_BYTES, 413),
])
def test_rejects_bad_uploads_without_history(setup, data, status):
    client, _ = setup
    add_contract(client)
    response = upload(client, data)
    assert response.status_code == status
    assert response.json()["detail"]
    assert client.get("/api/validations").json() == []


def test_unknown_contract_and_frontend(setup):
    client, _ = setup
    assert upload(client, b"id\n1\n", contract_id=99).status_code == 404
    assert client.get("/").status_code == 200
    assert "Create a contract" in client.get("/").text
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/docs").status_code == 200
    assert "/api/validate" in client.get("/openapi.json").json()["paths"]
