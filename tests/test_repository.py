import pytest
import app.repository as repo
from app.exceptions import RecordNotFoundError, InvalidFieldError


@pytest.fixture(autouse=True)
def isolate_data_file(tmp_path, monkeypatch):
    monkeypatch.setattr(repo, "DATA_FILE", str(tmp_path / "records.json"))


# ── get_all ──────────────────────────────────────────────────────────────────

def test_get_all_empty_when_no_file():
    assert repo.get_all() == []


def test_get_all_returns_all_records():
    repo.create("A", "a@a.com", "010-0000-0001")
    repo.create("B", "b@b.com", "010-0000-0002")
    assert len(repo.get_all()) == 2


# ── find_by_id ───────────────────────────────────────────────────────────────

def test_find_by_id_found():
    created = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    result = repo.find_by_id(created["id"][:8])
    assert result is not None
    assert result["name"] == "홍길동"


def test_find_by_id_not_found():
    assert repo.find_by_id("00000000") is None


# ── find_by_name ─────────────────────────────────────────────────────────────

def test_find_by_name_found():
    repo.create("홍길동", "hong@example.com", "010-1234-5678")
    repo.create("김철수", "kim@example.com", "010-9876-5432")
    result = repo.find_by_name("홍")
    assert len(result) == 1
    assert result[0]["name"] == "홍길동"


def test_find_by_name_not_found():
    repo.create("홍길동", "hong@example.com", "010-1234-5678")
    assert repo.find_by_name("없는이름") == []


# ── create ───────────────────────────────────────────────────────────────────

def test_create_adds_record():
    before = len(repo.get_all())
    repo.create("홍길동", "hong@example.com", "010-1234-5678")
    assert len(repo.get_all()) == before + 1


def test_create_returns_new_record():
    record = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    assert set(record.keys()) == {"id", "name", "email", "phone", "created_at"}
    assert record["name"] == "홍길동"


def test_create_persists_to_file(tmp_path, monkeypatch):
    path = tmp_path / "records2.json"
    monkeypatch.setattr(repo, "DATA_FILE", str(path))
    repo.create("홍길동", "hong@example.com", "010-1234-5678")
    assert path.exists()
    from json_lib import load
    records = load(str(path))
    assert len(records) == 1
    assert records[0]["name"] == "홍길동"


# ── update ───────────────────────────────────────────────────────────────────

def test_update_name():
    created = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    repo.update(created["id"][:8], "name", "홍길순")
    found = repo.find_by_id(created["id"][:8])
    assert found["name"] == "홍길순"


def test_update_email():
    created = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    repo.update(created["id"][:8], "email", "new@example.com")
    found = repo.find_by_id(created["id"][:8])
    assert found["email"] == "new@example.com"


def test_update_phone():
    created = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    repo.update(created["id"][:8], "phone", "010-9999-8888")
    found = repo.find_by_id(created["id"][:8])
    assert found["phone"] == "010-9999-8888"


def test_update_not_found():
    with pytest.raises(RecordNotFoundError):
        repo.update("00000000", "name", "홍길순")


def test_update_invalid_field():
    created = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    with pytest.raises(InvalidFieldError):
        repo.update(created["id"][:8], "id", "hacked")


# ── delete ───────────────────────────────────────────────────────────────────

def test_delete_removes_record():
    created = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    before = len(repo.get_all())
    repo.delete(created["id"][:8])
    assert len(repo.get_all()) == before - 1


def test_delete_returns_deleted_record():
    created = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    deleted = repo.delete(created["id"][:8])
    assert deleted["name"] == "홍길동"


def test_delete_not_found():
    with pytest.raises(RecordNotFoundError):
        repo.delete("00000000")
