import json
import pytest
from pathlib import Path

from json_lib.writer import save
from json_lib.exceptions import JsonSerializeError


def test_save_creates_file(tmp_path):
    dest = tmp_path / "result.json"
    save({"key": "value"}, str(dest))
    assert dest.exists()


def test_save_creates_directories(tmp_path):
    dest = tmp_path / "a" / "b" / "result.json"
    save({"key": "value"}, str(dest))
    assert dest.exists()


def test_save_content_correct(tmp_path):
    dest = tmp_path / "result.json"
    data = {"name": "Alice", "age": 30}
    save(data, str(dest))
    loaded = json.loads(dest.read_text(encoding="utf-8"))
    assert loaded == data


def test_save_overwrite_false(tmp_path):
    dest = tmp_path / "result.json"
    dest.write_text("{}", encoding="utf-8")
    with pytest.raises(FileExistsError):
        save({"new": "data"}, str(dest), overwrite=False)


def test_save_overwrite_true(tmp_path):
    dest = tmp_path / "result.json"
    dest.write_text('{"old": 1}', encoding="utf-8")
    save({"new": 2}, str(dest), overwrite=True)
    loaded = json.loads(dest.read_text(encoding="utf-8"))
    assert loaded == {"new": 2}


def test_save_non_serializable(tmp_path):
    dest = tmp_path / "result.json"
    with pytest.raises(JsonSerializeError):
        save({"bad": object()}, str(dest))


def test_save_korean(tmp_path):
    dest = tmp_path / "result.json"
    save({"이름": "홍길동"}, str(dest))
    raw = dest.read_text(encoding="utf-8")
    assert "홍길동" in raw
    assert "\\u" not in raw
