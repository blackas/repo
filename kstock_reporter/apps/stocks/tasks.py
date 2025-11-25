"""
주식 데이터 동기화 Celery 태스크

KRX API를 통해 주식 종목 마스터 데이터와 일별 가격 데이터를 동기화합니다.
"""
import logging
from datetime import date
from celery import shared_task

from .services import sync_stock_master_from_krx, sync_daily_prices_from_krx
from apps.common.exceptions import StockDataFetchError

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_stock_master_task(self, target_date_str: str | None = None):
    """
    주식 종목 마스터 데이터 동기화 태스크

    Args:
        target_date_str: 동기화할 날짜 (YYYY-MM-DD 형식), None이면 오늘 날짜

    Returns:
        dict: 성공 여부, 동기화된 종목 수, 날짜

    Raises:
        Retry: StockDataFetchError 발생 시 재시도
    """
    try:
        if target_date_str:
            target_date = date.fromisoformat(target_date_str)
        else:
            target_date = date.today()

        logger.info(f"[Task] Starting stock master sync for {target_date}")
        count = sync_stock_master_from_krx(target_date)
        logger.info(f"[Task] Completed stock master sync: {count} stocks")
        return {"success": True, "count": count, "date": target_date.isoformat()}

    except StockDataFetchError as exc:
        logger.error(f"[Task] Stock master sync failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)
    except Exception as exc:
        logger.error(f"[Task] Unexpected error in stock master sync: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_daily_prices_task(self, target_date_str: str | None = None):
    """
    일별 주가 데이터 동기화 태스크

    Args:
        target_date_str: 동기화할 날짜 (YYYY-MM-DD 형식), None이면 오늘 날짜

    Returns:
        dict: 성공 여부, 동기화된 가격 데이터 수, 날짜

    Raises:
        Retry: StockDataFetchError 발생 시 재시도
    """
    try:
        if target_date_str:
            target_date = date.fromisoformat(target_date_str)
        else:
            target_date = date.today()

        logger.info(f"[Task] Starting daily price sync for {target_date}")
        count = sync_daily_prices_from_krx(target_date)
        logger.info(f"[Task] Completed daily price sync: {count} prices")
        return {"success": True, "count": count, "date": target_date.isoformat()}

    except StockDataFetchError as exc:
        logger.error(f"[Task] Daily price sync failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)
    except Exception as exc:
        logger.error(f"[Task] Unexpected error in daily price sync: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)
