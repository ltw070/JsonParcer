class AppError(Exception):
    """앱 레이어 최상위 예외"""


class RecordNotFoundError(AppError):
    """ID로 레코드를 찾지 못함"""


class InvalidFieldError(AppError):
    """수정 불가 필드 지정"""
