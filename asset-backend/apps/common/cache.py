"""
Redis 캐싱 유틸리티
"""
import logging
import json
import pickle
from functools import wraps
from typing import Any, Callable, Optional
from datetime import timedelta

from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

# 캐시 키 프리픽스
CACHE_PREFIX = "noah-asset:"

# 기본 캐시 타임아웃 (초)
DEFAULT_TIMEOUT = 60 * 15  # 15분


def make_cache_key(*args, **kwargs) -> str:
    """
    캐시 키 생성
    """
    key_parts = [str(arg) for arg in args]
    if kwargs:
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return CACHE_PREFIX + ":".join(key_parts)


def cache_result(
    timeout: int = DEFAULT_TIMEOUT,
    key_prefix: str = "",
    use_args: bool = True,
):
    """
    함수 결과를 캐싱하는 데코레이터

    Args:
        timeout: 캐시 유효 시간 (초)
        key_prefix: 캐시 키 프리픽스
        use_args: 함수 인자를 캐시 키에 포함할지 여부
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 캐시 키 생성
            if use_args:
                cache_key = make_cache_key(
                    key_prefix or func.__name__,
                    *args,
                    **{k: v for k, v in kwargs.items() if k != "use_cache"}
                )
            else:
                cache_key = make_cache_key(key_prefix or func.__name__)

            # 캐시 사용 여부 확인
            use_cache = kwargs.pop("use_cache", True)

            if not use_cache:
                logger.debug(f"Cache disabled for {func.__name__}")
                return func(*args, **kwargs)

            # 캐시에서 조회
            try:
                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value
            except Exception as e:
                logger.warning(f"Cache get error: {e}")

            # 함수 실행
            logger.debug(f"Cache miss: {cache_key}")
            result = func(*args, **kwargs)

            # 캐시에 저장
            try:
                cache.set(cache_key, result, timeout)
                logger.debug(f"Cache set: {cache_key}, timeout={timeout}")
            except Exception as e:
                logger.warning(f"Cache set error: {e}")

            return result

        return wrapper
    return decorator


def invalidate_cache(key_prefix: str, *args, **kwargs):
    """
    특정 캐시 무효화
    """
    cache_key = make_cache_key(key_prefix, *args, **kwargs)
    try:
        cache.delete(cache_key)
        logger.info(f"Cache invalidated: {cache_key}")
    except Exception as e:
        logger.warning(f"Cache delete error: {e}")


def invalidate_pattern(pattern: str):
    """
    패턴에 맞는 캐시 무효화
    Redis 전용 기능
    """
    try:
        from django_redis import get_redis_connection
        conn = get_redis_connection("default")
        keys = conn.keys(f"{CACHE_PREFIX}{pattern}*")
        if keys:
            conn.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache keys matching pattern: {pattern}")
    except Exception as e:
        logger.warning(f"Pattern invalidation error: {e}")


def get_or_set_cache(
    key: str,
    callable_func: Callable,
    timeout: int = DEFAULT_TIMEOUT,
) -> Any:
    """
    캐시에서 값을 가져오거나, 없으면 함수를 실행하여 캐시에 저장
    """
    cache_key = make_cache_key(key)

    try:
        cached_value = cache.get(cache_key)
        if cached_value is not None:
            logger.debug(f"Cache hit: {cache_key}")
            return cached_value
    except Exception as e:
        logger.warning(f"Cache get error: {e}")

    result = callable_func()

    try:
        cache.set(cache_key, result, timeout)
        logger.debug(f"Cache set: {cache_key}")
    except Exception as e:
        logger.warning(f"Cache set error: {e}")

    return result


class CacheManager:
    """
    캐시 관리 클래스
    """

    @staticmethod
    def get_stock_price_key(stock_code: str, date: str) -> str:
        """주식 가격 캐시 키"""
        return f"stock:price:{stock_code}:{date}"

    @staticmethod
    def get_stock_list_key(market: Optional[str] = None) -> str:
        """주식 목록 캐시 키"""
        if market:
            return f"stock:list:{market}"
        return "stock:list:all"

    @staticmethod
    def get_watchlist_key(user_id: int) -> str:
        """관심목록 캐시 키"""
        return f"watchlist:user:{user_id}"

    @staticmethod
    def get_report_key(user_id: int, date: str) -> str:
        """리포트 캐시 키"""
        return f"report:user:{user_id}:{date}"

    @staticmethod
    def invalidate_user_caches(user_id: int):
        """사용자 관련 캐시 무효화"""
        invalidate_pattern(f"watchlist:user:{user_id}")
        invalidate_pattern(f"report:user:{user_id}")

    @staticmethod
    def invalidate_stock_caches(stock_code: str):
        """주식 관련 캐시 무효화"""
        invalidate_pattern(f"stock:price:{stock_code}")
        invalidate_pattern("stock:list")
