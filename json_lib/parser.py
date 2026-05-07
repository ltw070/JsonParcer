import json
from pathlib import Path

from .exceptions import JsonParseError


def parse(json_str: str) -> dict | list:
    if not isinstance(json_str, str):
        raise JsonParseError(f"입력값이 str이어야 하지만 {type(json_str).__name__} 입니다.")
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise JsonParseError(f"JSON 파싱 실패: {e}") from e


def load(file_path: str, encoding: str = "utf-8") -> dict | list:
    content = Path(file_path).read_text(encoding=encoding)
    return parse(content)
