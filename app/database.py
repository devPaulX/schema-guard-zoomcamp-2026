"""SQLite storage for contracts and validation history."""

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "schemaguard.db"


@contextmanager
def connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                required_columns TEXT NOT NULL,
                missing_value_threshold REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS validations (
                id INTEGER PRIMARY KEY,
                created_at TEXT NOT NULL,
                contract_id INTEGER NOT NULL REFERENCES contracts(id),
                filename TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('PASS', 'FAIL')),
                reasons TEXT NOT NULL
            );
            """
        )


def contract_from_row(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "required_columns": json.loads(row["required_columns"]),
        "missing_value_threshold": row["missing_value_threshold"],
    }


def list_contracts(db_path: Path) -> list[dict]:
    with connect(db_path) as connection:
        rows = connection.execute("SELECT * FROM contracts ORDER BY id DESC").fetchall()
    return [contract_from_row(row) for row in rows]


def get_contract(db_path: Path, contract_id: int) -> dict | None:
    with connect(db_path) as connection:
        row = connection.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,)).fetchone()
    return contract_from_row(row) if row else None


def create_contract(db_path: Path, name: str, columns: list[str], threshold: float) -> dict:
    with connect(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO contracts (name, required_columns, missing_value_threshold) VALUES (?, ?, ?)",
            (name, json.dumps(columns), threshold),
        )
        contract_id = cursor.lastrowid
    return get_contract(db_path, contract_id)


def validation_from_row(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "contract_id": row["contract_id"],
        "contract_name": row["contract_name"],
        "filename": row["filename"],
        "status": row["status"],
        "reasons": json.loads(row["reasons"]),
    }


def list_validations(db_path: Path) -> list[dict]:
    with connect(db_path) as connection:
        rows = connection.execute(
            """SELECT v.*, c.name AS contract_name FROM validations AS v
               JOIN contracts AS c ON c.id = v.contract_id ORDER BY v.id DESC"""
        ).fetchall()
    return [validation_from_row(row) for row in rows]


def save_validation(db_path: Path, contract_id: int, filename: str, status: str, reasons: list[str]) -> dict:
    created_at = datetime.now(timezone.utc).isoformat()
    with connect(db_path) as connection:
        cursor = connection.execute(
            """INSERT INTO validations (created_at, contract_id, filename, status, reasons)
               VALUES (?, ?, ?, ?, ?)""",
            (created_at, contract_id, filename, status, json.dumps(reasons)),
        )
        row = connection.execute(
            """SELECT v.*, c.name AS contract_name FROM validations AS v
               JOIN contracts AS c ON c.id = v.contract_id WHERE v.id = ?""",
            (cursor.lastrowid,),
        ).fetchone()
    return validation_from_row(row)
