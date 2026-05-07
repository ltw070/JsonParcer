import json
from pathlib import Path

from .exceptions import JsonSerializeError


def save(
    data: dict | list,
    file_path: str,
    encoding: str = "utf-8",
    indent: int = 2,
    ensure_ascii: bool = False,
    overwrite: bool = True,
) -> None:
    path = Path(file_path)

    if not overwrite and path.exists():
        raise FileExistsError(f"파일이 이미 존재합니다: {file_path}")

    try:
        content = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
    except TypeError as e:
        raise JsonSerializeError(f"JSON 직렬화 실패: {e}") from e

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=encoding)
