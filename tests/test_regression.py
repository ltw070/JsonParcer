"""Regression Tests — 기존 CRUD 동작이 변경 후에도 깨지지 않음을 보장."""
import json
import pytest
import app.repository as repo
from app.exceptions import RecordNotFoundError
from app.menu import handle_list, handle_create, handle_delete
from json_lib import load
from unittest.mock import patch
from io import StringIO


@pytest.fixture(autouse=True)
def isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(repo, "DATA_FILE", str(tmp_path / "records.json"))


# ── R-Create ──────────────────────────────────────────────────────────────────

def test_create_returns_complete_record():
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    assert set(r.keys()) == {"id", "name", "email", "phone", "created_at"}


def test_create_persists_to_file(tmp_path, monkeypatch):
    path = tmp_path / "r.json"
    monkeypatch.setattr(repo, "DATA_FILE", str(path))
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    on_disk = load(str(path))
    assert any(rec["id"] == r["id"] for rec in on_disk)


def test_create_multiple_records():
    repo.create("A", "a@a.com", "010-0000-0001")
    repo.create("B", "b@b.com", "010-0000-0002")
    repo.create("C", "c@c.com", "010-0000-0003")
    assert len(repo.get_all()) == 3


def test_create_id_is_unique():
    ids = {repo.create(f"U{i}", f"u{i}@x.com", "010-0000-0000")["id"] for i in range(5)}
    assert len(ids) == 5


# ── R-Read ────────────────────────────────────────────────────────────────────

def test_get_all_no_file():
    assert repo.get_all() == []


def test_get_all_after_create():
    for i in range(3):
        repo.create(f"N{i}", f"n{i}@x.com", "010-0000-0000")
    assert len(repo.get_all()) == 3


def test_find_by_id_full():
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    assert repo.find_by_id(r["id"])["id"] == r["id"]


def test_find_by_id_prefix():
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    assert repo.find_by_id(r["id"][:8])["name"] == "홍길동"


def test_find_by_id_missing():
    assert repo.find_by_id("00000000") is None


def test_find_by_name_exact():
    repo.create("홍길동", "hong@example.com", "010-1234-5678")
    assert len(repo.find_by_name("홍길동")) == 1


def test_find_by_name_partial():
    repo.create("홍길동", "hong@example.com", "010-1234-5678")
    repo.create("홍길순", "hongs@example.com", "010-0000-0001")
    repo.create("김철수", "kim@example.com", "010-0000-0002")
    assert len(repo.find_by_name("홍")) == 2


def test_find_by_name_missing():
    repo.create("홍길동", "hong@example.com", "010-1234-5678")
    assert repo.find_by_name("없는이름") == []


# ── R-Update ──────────────────────────────────────────────────────────────────

def test_update_name():
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    repo.update(r["id"][:8], "name", "홍길순")
    assert repo.find_by_id(r["id"][:8])["name"] == "홍길순"


def test_update_email():
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    repo.update(r["id"][:8], "email", "new@example.com")
    assert repo.find_by_id(r["id"][:8])["email"] == "new@example.com"


def test_update_phone():
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    repo.update(r["id"][:8], "phone", "010-9999-9999")
    assert repo.find_by_id(r["id"][:8])["phone"] == "010-9999-9999"


def test_update_persists_to_file(tmp_path, monkeypatch):
    path = tmp_path / "u.json"
    monkeypatch.setattr(repo, "DATA_FILE", str(path))
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    repo.update(r["id"][:8], "email", "updated@example.com")
    on_disk = load(str(path))
    assert on_disk[0]["email"] == "updated@example.com"


def test_update_other_records_unchanged():
    r1 = repo.create("A", "a@a.com", "010-0000-0001")
    r2 = repo.create("B", "b@b.com", "010-0000-0002")
    repo.update(r1["id"][:8], "name", "A-Updated")
    assert repo.find_by_id(r2["id"][:8])["name"] == "B"


# ── R-Delete ──────────────────────────────────────────────────────────────────

def test_delete_removes_from_list():
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    before = len(repo.get_all())
    repo.delete(r["id"][:8])
    assert len(repo.get_all()) == before - 1


def test_delete_returns_record():
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    deleted = repo.delete(r["id"][:8])
    assert deleted["name"] == "홍길동"


def test_delete_persists_to_file(tmp_path, monkeypatch):
    path = tmp_path / "d.json"
    monkeypatch.setattr(repo, "DATA_FILE", str(path))
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    repo.delete(r["id"][:8])
    on_disk = load(str(path))
    assert on_disk == []


def test_delete_other_records_unchanged():
    r1 = repo.create("A", "a@a.com", "010-0000-0001")
    r2 = repo.create("B", "b@b.com", "010-0000-0002")
    repo.delete(r1["id"][:8])
    remaining = repo.get_all()
    assert len(remaining) == 1
    assert remaining[0]["name"] == "B"


# ── R-Menu ────────────────────────────────────────────────────────────────────

def test_handle_list_empty(capsys):
    handle_list()
    assert "등록된 연락처가 없습니다." in capsys.readouterr().out


def test_handle_list_with_records(capsys):
    repo.create("홍길동", "hong@example.com", "010-1234-5678")
    repo.create("김철수", "kim@example.com", "010-9876-5432")
    handle_list()
    out = capsys.readouterr().out
    assert "총 2건" in out


def test_handle_create_success(capsys):
    inputs = iter(["홍길동", "hong@example.com", "010-1234-5678"])
    with patch("builtins.input", side_effect=inputs):
        handle_create()
    assert "저장되었습니다" in capsys.readouterr().out


def test_handle_delete_cancel(capsys):
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    inputs = iter([r["id"][:8], "n"])
    with patch("builtins.input", side_effect=inputs):
        handle_delete()
    assert "취소" in capsys.readouterr().out
    assert repo.find_by_id(r["id"][:8]) is not None
