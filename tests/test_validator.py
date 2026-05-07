import pytest

from json_lib.validator import validate
from json_lib.exceptions import JsonValidationError


def test_validate_success():
    data = {"name": "Alice", "age": 30, "scores": [90, 95]}
    schema = {"name": str, "age": int, "scores": list}
    validate(data, schema)  # 예외 없이 통과해야 함


def test_validate_missing_key():
    data = {"name": "Alice"}
    schema = {"name": str, "age": int}
    with pytest.raises(JsonValidationError):
        validate(data, schema)


def test_validate_wrong_type():
    data = {"name": "Alice", "age": "thirty"}
    schema = {"name": str, "age": int}
    with pytest.raises(JsonValidationError):
        validate(data, schema)


def test_validate_error_message_key():
    data = {"name": "Alice"}
    schema = {"name": str, "age": int}
    with pytest.raises(JsonValidationError, match="age"):
        validate(data, schema)


def test_validate_error_message_type():
    data = {"name": "Alice", "age": "thirty"}
    schema = {"name": str, "age": int}
    with pytest.raises(JsonValidationError, match="age"):
        validate(data, schema)
