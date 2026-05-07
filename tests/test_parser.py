import json
import pytest
from pathlib import Path

from json_lib.parser import parse, load
from json_lib.exceptions import JsonParseError


def test_parse_dict():
    result = parse('{"name": "Alice", "age": 30}')
    assert result == {"name": "Alice", "age": 30}


def test_parse_list():
    result = parse('[1, 2, 3]')
    assert result == [1, 2, 3]


def test_parse_invalid_json():
    with pytest.raises(JsonParseError):
        parse("{invalid json}")


def test_parse_non_string():
    with pytest.raises(JsonParseError):
        parse(12345)


def test_load_file(tmp_path):
    f = tmp_path / "sample.json"
    f.write_text('{"user": "Bob", "score": 95}', encoding="utf-8")
    result = load(str(f))
    assert result == {"user": "Bob", "score": 95}


def test_load_file_not_found():
    with pytest.raises(FileNotFoundError):
        load("nonexistent_file.json")


def test_load_invalid_content(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text("not valid json", encoding="utf-8")
    with pytest.raises(JsonParseError):
        load(str(f))
