"""
주식 데이터 동기화 Celery 태스크

KRX API를 통해 주식 종목 마스터 데이터와 일별 가격 데이터를 동기화합니다.
"""
import logging
from datetime import date, timedelta
from celery import shared_task

from .services import (
    sync_stock_master_from_krx,
    sync_daily_prices_from_krx,
    aggregate_weekly_prices,
    aggregate_monthly_prices,
    aggregate_yearly_prices,
)
from .models import Stock
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


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def aggregate_weekly_prices_task(
    self,
    stock_code: str | None = None,
    start_date_str: str | None = None,
    end_date_str: str | None = None
):
    """
    주봉 캔들 집계 태스크

    Args:
        stock_code: 집계할 종목 코드 (None이면 모든 활성 종목)
        start_date_str: 집계 시작일 (YYYY-MM-DD), None이면 1년 전부터
        end_date_str: 집계 종료일 (YYYY-MM-DD), None이면 오늘까지

    Returns:
        dict: 성공 여부, 집계된 종목 수, 총 주봉 수
    """
    try:
        # 날짜 설정
        if end_date_str:
            end_date = date.fromisoformat(end_date_str)
        else:
            end_date = date.today()

        if start_date_str:
            start_date = date.fromisoformat(start_date_str)
        else:
            start_date = end_date - timedelta(days=365)

        # 종목 조회
        if stock_code:
            stocks = Stock.objects.filter(code=stock_code, is_active=True)
        else:
            stocks = Stock.objects.filter(is_active=True)

        logger.info(f"[Task] Starting weekly aggregation for {stocks.count()} stocks")

        total_count = 0
        success_count = 0

        for stock in stocks:
            try:
                count = aggregate_weekly_prices(stock, start_date, end_date)
                total_count += count
                success_count += 1
            except Exception as e:
                logger.error(f"[Task] Failed to aggregate weekly prices for {stock.code}: {e}")
                continue

        logger.info(f"[Task] Completed weekly aggregation: {success_count} stocks, {total_count} candles")
        return {
            "success": True,
            "stocks_count": success_count,
            "total_candles": total_count,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }

    except StockDataFetchError as exc:
        logger.error(f"[Task] Weekly aggregation failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)
    except Exception as exc:
        logger.error(f"[Task] Unexpected error in weekly aggregation: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def aggregate_monthly_prices_task(
    self,
    stock_code: str | None = None,
    start_date_str: str | None = None,
    end_date_str: str | None = None
):
    """
    월봉 캔들 집계 태스크

    Args:
        stock_code: 집계할 종목 코드 (None이면 모든 활성 종목)
        start_date_str: 집계 시작일 (YYYY-MM-DD), None이면 1년 전부터
        end_date_str: 집계 종료일 (YYYY-MM-DD), None이면 오늘까지

    Returns:
        dict: 성공 여부, 집계된 종목 수, 총 월봉 수
    """
    try:
        # 날짜 설정
        if end_date_str:
            end_date = date.fromisoformat(end_date_str)
        else:
            end_date = date.today()

        if start_date_str:
            start_date = date.fromisoformat(start_date_str)
        else:
            start_date = end_date - timedelta(days=365)

        # 종목 조회
        if stock_code:
            stocks = Stock.objects.filter(code=stock_code, is_active=True)
        else:
            stocks = Stock.objects.filter(is_active=True)

        logger.info(f"[Task] Starting monthly aggregation for {stocks.count()} stocks")

        total_count = 0
        success_count = 0

        for stock in stocks:
            try:
                count = aggregate_monthly_prices(stock, start_date, end_date)
                total_count += count
                success_count += 1
            except Exception as e:
                logger.error(f"[Task] Failed to aggregate monthly prices for {stock.code}: {e}")
                continue

        logger.info(f"[Task] Completed monthly aggregation: {success_count} stocks, {total_count} candles")
        return {
            "success": True,
            "stocks_count": success_count,
            "total_candles": total_count,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }

    except StockDataFetchError as exc:
        logger.error(f"[Task] Monthly aggregation failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)
    except Exception as exc:
        logger.error(f"[Task] Unexpected error in monthly aggregation: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def aggregate_yearly_prices_task(
    self,
    stock_code: str | None = None,
    start_date_str: str | None = None,
    end_date_str: str | None = None
):
    """
    연봉 캔들 집계 태스크

    Args:
        stock_code: 집계할 종목 코드 (None이면 모든 활성 종목)
        start_date_str: 집계 시작일 (YYYY-MM-DD), None이면 5년 전부터
        end_date_str: 집계 종료일 (YYYY-MM-DD), None이면 오늘까지

    Returns:
        dict: 성공 여부, 집계된 종목 수, 총 연봉 수
    """
    try:
        # 날짜 설정
        if end_date_str:
            end_date = date.fromisoformat(end_date_str)
        else:
            end_date = date.today()

        if start_date_str:
            start_date = date.fromisoformat(start_date_str)
        else:
            start_date = end_date - timedelta(days=365*5)  # 5년 전

        # 종목 조회
        if stock_code:
            stocks = Stock.objects.filter(code=stock_code, is_active=True)
        else:
            stocks = Stock.objects.filter(is_active=True)

        logger.info(f"[Task] Starting yearly aggregation for {stocks.count()} stocks")

        total_count = 0
        success_count = 0

        for stock in stocks:
            try:
                count = aggregate_yearly_prices(stock, start_date, end_date)
                total_count += count
                success_count += 1
            except Exception as e:
                logger.error(f"[Task] Failed to aggregate yearly prices for {stock.code}: {e}")
                continue

        logger.info(f"[Task] Completed yearly aggregation: {success_count} stocks, {total_count} candles")
        return {
            "success": True,
            "stocks_count": success_count,
            "total_candles": total_count,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }

    except StockDataFetchError as exc:
        logger.error(f"[Task] Yearly aggregation failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)
    except Exception as exc:
        logger.error(f"[Task] Unexpected error in yearly aggregation: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)
