"""Safety Tests — 비정상 입력·손상 파일·경계값에서 앱이 안전하게 동작함을 보장."""
import json
import pytest
import app.repository as repo
from app.exceptions import RecordNotFoundError, InvalidFieldError
from app.menu import handle_update, handle_delete, handle_search
from json_lib.exceptions import JsonParseError
from pathlib import Path
from unittest.mock import patch


@pytest.fixture(autouse=True)
def isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(repo, "DATA_FILE", str(tmp_path / "records.json"))


# ── S-Input: 입력값 경계 ──────────────────────────────────────────────────────

def test_create_with_special_chars():
    r = repo.create("홍!@#$%^&*()", "test!@#@example.com", "010-!@#-5678")
    found = repo.find_by_id(r["id"][:8])
    assert found["name"] == "홍!@#$%^&*()"


def test_create_with_emoji():
    r = repo.create("홍길동😊🎉", "emoji@example.com", "010-1234-5678")
    found = repo.find_by_id(r["id"][:8])
    assert found["name"] == "홍길동😊🎉"


def test_create_with_very_long_strings():
    long_name = "가" * 1000
    r = repo.create(long_name, "long@example.com", "010-1234-5678")
    found = repo.find_by_id(r["id"][:8])
    assert found["name"] == long_name


def test_create_with_script_tag():
    r = repo.create("<script>alert(1)</script>", "xss@example.com", "010-0000-0000")
    found = repo.find_by_id(r["id"][:8])
    assert found["name"] == "<script>alert(1)</script>"


def test_create_with_quotes_and_backslash():
    r = repo.create('홍"길\\동\'', 'q"uote@example.com', "010-0000-0000")
    found = repo.find_by_id(r["id"][:8])
    assert found["name"] == '홍"길\\동\''
    assert found["email"] == 'q"uote@example.com'


def test_create_with_newline_in_field():
    r = repo.create("홍길동\n개행", "newline@example.com", "010-0000-0000")
    found = repo.find_by_id(r["id"][:8])
    assert found["name"] == "홍길동\n개행"


# ── S-NotFound: 없는 대상 접근 ───────────────────────────────────────────────

def test_update_nonexistent_id():
    with pytest.raises(RecordNotFoundError):
        repo.update("00000000", "name", "테스트")


def test_delete_nonexistent_id():
    with pytest.raises(RecordNotFoundError):
        repo.delete("00000000")


def test_find_by_id_empty_prefix():
    r1 = repo.create("A", "a@a.com", "010-0000-0001")
    r2 = repo.create("B", "b@b.com", "010-0000-0002")
    # 빈 접두사는 모든 ID와 매칭 → 첫 번째 레코드 반환
    result = repo.find_by_id("")
    assert result is not None
    assert result["id"] in (r1["id"], r2["id"])


# ── S-InvalidField: 수정 불가 필드 ───────────────────────────────────────────

def test_update_id_field():
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    with pytest.raises(InvalidFieldError):
        repo.update(r["id"][:8], "id", "hacked-id")


def test_update_created_at_field():
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    with pytest.raises(InvalidFieldError):
        repo.update(r["id"][:8], "created_at", "2000-01-01T00:00:00")


def test_update_unknown_field():
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    with pytest.raises(InvalidFieldError):
        repo.update(r["id"][:8], "nonexistent_field", "value")


# ── S-FileCorrupt: 파일 손상 ─────────────────────────────────────────────────

def test_load_corrupted_json(tmp_path, monkeypatch):
    path = tmp_path / "bad.json"
    path.write_text("this is not json {{{", encoding="utf-8")
    monkeypatch.setattr(repo, "DATA_FILE", str(path))
    with pytest.raises(JsonParseError):
        repo.get_all()


def test_load_empty_file(tmp_path, monkeypatch):
    path = tmp_path / "empty.json"
    path.write_text("", encoding="utf-8")
    monkeypatch.setattr(repo, "DATA_FILE", str(path))
    with pytest.raises(JsonParseError):
        repo.get_all()


def test_load_json_object_not_list(tmp_path, monkeypatch):
    path = tmp_path / "obj.json"
    path.write_text('{"key": "value"}', encoding="utf-8")
    monkeypatch.setattr(repo, "DATA_FILE", str(path))
    # dict가 반환되면 이후 list 연산에서 TypeError 발생할 수 있음 — 안전하게 처리되는지 확인
    result = repo.get_all()
    # dict를 반환하더라도 앱이 크래시 없이 값을 돌려줘야 함
    assert result is not None


# ── S-Boundary: 경계값 ───────────────────────────────────────────────────────

def test_delete_last_record(tmp_path, monkeypatch):
    path = tmp_path / "last.json"
    monkeypatch.setattr(repo, "DATA_FILE", str(path))
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    repo.delete(r["id"][:8])
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk == []


def test_create_100_records():
    for i in range(100):
        repo.create(f"사용자{i:03d}", f"user{i}@example.com", f"010-{i:04d}-{i:04d}")
    assert len(repo.get_all()) == 100


def test_duplicate_name():
    repo.create("홍길동", "hong1@example.com", "010-0000-0001")
    repo.create("홍길동", "hong2@example.com", "010-0000-0002")
    results = repo.find_by_name("홍길동")
    assert len(results) == 2


def test_id_prefix_ambiguity(monkeypatch):
    # 두 레코드의 ID 앞자리가 동일한 상황을 강제로 만들어 첫 번째 반환 확인
    import uuid
    fixed_ids = ["aaaaaaaa-0000-4000-8000-000000000001",
                 "aaaaaaaa-0000-4000-8000-000000000002"]
    id_iter = iter(fixed_ids)
    monkeypatch.setattr(uuid, "uuid4", lambda: type("F", (), {"__str__": lambda s: next(id_iter)})())
    r1 = repo.create("첫번째", "first@example.com", "010-0000-0001")
    r2 = repo.create("두번째", "second@example.com", "010-0000-0002")
    result = repo.find_by_id("aaaaaaaa")
    assert result["name"] == "첫번째"


# ── S-Menu: UI 안전성 ─────────────────────────────────────────────────────────

def test_handle_update_not_found(capsys):
    inputs = iter(["00000000"])
    with patch("builtins.input", side_effect=inputs):
        handle_update()
    assert "찾을 수 없습니다" in capsys.readouterr().out


def test_handle_delete_not_found(capsys):
    inputs = iter(["00000000"])
    with patch("builtins.input", side_effect=inputs):
        handle_delete()
    assert "찾을 수 없습니다" in capsys.readouterr().out


def test_handle_search_no_result(capsys):
    repo.create("홍길동", "hong@example.com", "010-1234-5678")
    inputs = iter(["2", "없는이름"])
    with patch("builtins.input", side_effect=inputs):
        handle_search()
    assert "검색 결과가 없습니다" in capsys.readouterr().out


def test_handle_update_invalid_field_choice(capsys):
    r = repo.create("홍길동", "hong@example.com", "010-1234-5678")
    inputs = iter([r["id"][:8], "9"])
    with patch("builtins.input", side_effect=inputs):
        handle_update()
    assert "올바른 항목을 선택해주세요" in capsys.readouterr().out
