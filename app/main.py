"""SchemaGuard HTTP API and dashboard."""

import math
import sqlite3
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, field_validator

from . import database
from .validation import InvalidCSV, MAX_CSV_BYTES, validate_csv


FRONTEND = Path(__file__).resolve().parent.parent / "frontend"


class ContractInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    required_columns: list[str]
    missing_value_threshold: float

    @field_validator("name")
    @classmethod
    def check_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Contract name must not be empty.")
        return value

    @field_validator("required_columns")
    @classmethod
    def check_columns(cls, value: list[str]) -> list[str]:
        if not value or any(not column.strip() for column in value):
            raise ValueError("Provide at least one nonempty required column name.")
        if len(value) != len(set(value)):
            raise ValueError("Required column names must be unique.")
        return value

    @field_validator("missing_value_threshold")
    @classmethod
    def check_threshold(cls, value: float) -> float:
        if not math.isfinite(value) or not 0 <= value <= 100:
            raise ValueError("Missing-value threshold must be between 0 and 100.")
        return value


def create_app(db_path: Path | None = None) -> FastAPI:
    path = db_path or database.DEFAULT_DB_PATH
    database.initialize(path)
    application = FastAPI(title="SchemaGuard", version="1.0.0")
    application.mount("/static", StaticFiles(directory=FRONTEND), name="static")

    @application.get("/")
    def dashboard() -> FileResponse:
        return FileResponse(FRONTEND / "index.html")

    @application.get("/api/health")
    def health() -> dict:
        return {"status": "ok"}

    @application.get("/api/contracts")
    def contracts() -> list[dict]:
        return database.list_contracts(path)

    @application.post("/api/contracts", status_code=201)
    def add_contract(payload: ContractInput) -> dict:
        try:
            return database.create_contract(
                path, payload.name, payload.required_columns, payload.missing_value_threshold
            )
        except sqlite3.IntegrityError as exc:
            raise HTTPException(status_code=409, detail="A contract with this name already exists.") from exc

    @application.get("/api/validations")
    def validations() -> list[dict]:
        return database.list_validations(path)

    @application.post("/api/validate", status_code=201)
    async def validate(contract_id: int = Form(...), file: UploadFile = File(...)) -> dict:
        contract = database.get_contract(path, contract_id)
        if contract is None:
            raise HTTPException(status_code=404, detail="Contract not found.")
        if not file.filename:
            raise HTTPException(status_code=400, detail="CSV filename is required.")
        contents = await file.read(MAX_CSV_BYTES + 1)
        if len(contents) > MAX_CSV_BYTES:
            raise HTTPException(status_code=413, detail="CSV file exceeds the 5 MiB limit.")
        try:
            result = validate_csv(
                contents, contract["required_columns"], contract["missing_value_threshold"]
            )
        except InvalidCSV as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        filename = file.filename.replace("\\", "/").split("/")[-1]
        return database.save_validation(path, contract_id, filename, result.status, result.reasons)

    return application


app = create_app()
