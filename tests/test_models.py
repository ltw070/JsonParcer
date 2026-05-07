import re
import pytest
from datetime import datetime

from app.models import create_record


def test_create_record_returns_dict():
    record = create_record("홍길동", "hong@example.com", "010-1234-5678")
    assert isinstance(record, dict)


def test_create_record_has_all_fields():
    record = create_record("홍길동", "hong@example.com", "010-1234-5678")
    assert set(record.keys()) == {"id", "name", "email", "phone", "created_at"}


def test_create_record_id_is_uuid_string():
    record = create_record("홍길동", "hong@example.com", "010-1234-5678")
    uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    assert re.match(uuid_pattern, record["id"])


def test_create_record_name_email_phone_match_input():
    record = create_record("홍길동", "hong@example.com", "010-1234-5678")
    assert record["name"] == "홍길동"
    assert record["email"] == "hong@example.com"
    assert record["phone"] == "010-1234-5678"


def test_create_record_created_at_is_iso_string():
    record = create_record("홍길동", "hong@example.com", "010-1234-5678")
    datetime.fromisoformat(record["created_at"])  # 파싱 실패 시 ValueError


def test_create_record_ids_are_unique():
    r1 = create_record("A", "a@a.com", "010-0000-0001")
    r2 = create_record("B", "b@b.com", "010-0000-0002")
    assert r1["id"] != r2["id"]
