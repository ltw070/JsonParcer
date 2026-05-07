class JsonLibraryError(Exception):
    """최상위 기본 예외"""


class JsonParseError(JsonLibraryError):
    """JSON 파싱 실패"""


class JsonSerializeError(JsonLibraryError):
    """JSON 직렬화 실패"""


class JsonValidationError(JsonLibraryError):
    """스키마 검증 실패"""
