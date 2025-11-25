"""
성능 최적화 데코레이터
"""
from functools import wraps
from django.db import connection
from django.test.utils import override_settings
import logging

logger = logging.getLogger(__name__)


def log_queries(func):
    """
    실행된 SQL 쿼리를 로깅하는 데코레이터
    개발 환경에서만 사용
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from django.conf import settings

        if not settings.DEBUG:
            return func(*args, **kwargs)

        # 쿼리 카운트 초기화
        initial_queries = len(connection.queries)

        # 함수 실행
        result = func(*args, **kwargs)

        # 실행된 쿼리 수
        executed_queries = len(connection.queries) - initial_queries

        logger.debug(f"{func.__name__} executed {executed_queries} queries")

        # 쿼리가 많으면 경고
        if executed_queries > 10:
            logger.warning(
                f"{func.__name__} executed {executed_queries} queries. "
                "Consider optimization."
            )

        # 개발 환경에서 쿼리 출력
        if executed_queries > 0:
            for query in connection.queries[initial_queries:]:
                logger.debug(f"SQL: {query['sql'][:100]}... ({query['time']}s)")

        return result

    return wrapper


def select_related_fields(*fields):
    """
    select_related를 자동으로 적용하는 데코레이터
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if hasattr(result, 'select_related'):
                return result.select_related(*fields)
            return result
        return wrapper
    return decorator


def prefetch_related_fields(*fields):
    """
    prefetch_related를 자동으로 적용하는 데코레이터
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if hasattr(result, 'prefetch_related'):
                return result.prefetch_related(*fields)
            return result
        return wrapper
    return decorator
