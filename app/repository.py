from pathlib import Path

from json_lib import load, save, validate
from app.models import create_record
from app.exceptions import RecordNotFoundError, InvalidFieldError

DATA_FILE = "data/records.json"

SCHEMA = {
    "id": str,
    "name": str,
    "email": str,
    "phone": str,
    "created_at": str,
}

UPDATABLE_FIELDS = {"name", "email", "phone"}


def get_all() -> list:
    if not Path(DATA_FILE).exists():
        return []
    return load(DATA_FILE)


def find_by_id(id_prefix: str) -> dict | None:
    return next(
        (r for r in get_all() if r["id"].startswith(id_prefix)), None
    )


def find_by_name(keyword: str) -> list:
    return [r for r in get_all() if keyword in r["name"]]


def create(name: str, email: str, phone: str) -> dict:
    record = create_record(name, email, phone)
    validate(record, SCHEMA)
    records = get_all()
    records.append(record)
    save(records, DATA_FILE)
    return record


def update(id_prefix: str, field: str, value: str) -> dict:
    if field not in UPDATABLE_FIELDS:
        raise InvalidFieldError(f"수정할 수 없는 필드입니다: {field}")
    records = get_all()
    for record in records:
        if record["id"].startswith(id_prefix):
            record[field] = value
            validate(record, SCHEMA)
            save(records, DATA_FILE)
            return record
    raise RecordNotFoundError(f"ID를 찾을 수 없습니다: {id_prefix}")


def delete(id_prefix: str) -> dict:
    records = get_all()
    for i, record in enumerate(records):
        if record["id"].startswith(id_prefix):
            removed = records.pop(i)
            save(records, DATA_FILE)
            return removed
    raise RecordNotFoundError(f"ID를 찾을 수 없습니다: {id_prefix}")
