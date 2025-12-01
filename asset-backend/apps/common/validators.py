import re
from django.core.exceptions import ValidationError


def validate_korean_phone_number(value: str):
    """
    한국 전화번호 형식 검증
    """
    pattern = r"^01[0-9]-\d{3,4}-\d{4}$"
    if not re.match(pattern, value):
        raise ValidationError(
            "올바른 전화번호 형식이 아닙니다. (예: 010-1234-5678)"
        )


def validate_stock_code(value: str):
    """
    주식 코드 형식 검증 (6자리 숫자)
    """
    if not re.match(r"^\d{6}$", value):
        raise ValidationError(
            "올바른 주식 코드 형식이 아닙니다. (6자리 숫자)"
        )


def validate_not_empty_string(value: str):
    """
    빈 문자열 검증
    """
    if not value or not value.strip():
        raise ValidationError("빈 문자열은 허용되지 않습니다.")
