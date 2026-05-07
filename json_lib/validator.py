from .exceptions import JsonValidationError


def validate(data: dict | list, schema: dict) -> None:
    if not isinstance(data, dict):
        raise JsonValidationError(f"data가 dict이어야 하지만 {type(data).__name__} 입니다.")

    for key, expected_type in schema.items():
        if key not in data:
            raise JsonValidationError(f"필수 키 '{key}' 이 데이터에 없습니다.")
        if not isinstance(data[key], expected_type):
            raise JsonValidationError(
                f"키 '{key}' 의 값이 {expected_type} 이어야 하지만 {type(data[key])} 입니다."
            )
