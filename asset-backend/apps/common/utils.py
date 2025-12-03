import logging
from functools import wraps
from typing import Any, Callable

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    함수 실행 실패 시 재시도하는 데코레이터

    Args:
        max_retries: 최대 재시도 횟수
        delay: 재시도 간 대기 시간(초)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import time

            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(delay)

            logger.error(f"{func.__name__} failed after {max_retries} attempts")
            raise last_exception

        return wrapper
    return decorator


def log_execution_time(func: Callable) -> Callable:
    """
    함수 실행 시간을 로깅하는 데코레이터
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        import time

        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time

        logger.info(f"{func.__name__} executed in {duration:.2f} seconds")
        return result

    return wrapper


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    민감한 데이터를 마스킹 처리

    Args:
        data: 마스킹할 데이터
        visible_chars: 보이는 문자 수

    Returns:
        마스킹된 문자열
    """
    if not data or len(data) <= visible_chars:
        return "*" * len(data) if data else ""

    visible_part = data[:visible_chars]
    masked_part = "*" * (len(data) - visible_chars)
    return visible_part + masked_part


def sanitize_phone_number(phone: str) -> str:
    """
    전화번호를 표준 형식으로 변환

    Args:
        phone: 입력 전화번호

    Returns:
        정제된 전화번호 (010-1234-5678)
    """
    # 숫자만 추출
    numbers = "".join(filter(str.isdigit, phone))

    if len(numbers) == 11:
        return f"{numbers[:3]}-{numbers[3:7]}-{numbers[7:]}"
    elif len(numbers) == 10:
        return f"{numbers[:3]}-{numbers[3:6]}-{numbers[6:]}"

    return phone
