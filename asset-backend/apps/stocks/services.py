import logging
from datetime import date
from django.db import transaction

from .models import Stock, DailyPrice
from apps.common.exceptions import StockDataFetchError
from apps.common.utils import retry_on_failure, log_execution_time

logger = logging.getLogger(__name__)


def format_krx_date(d: date) -> str:
    return d.strftime("%Y%m%d")


@log_execution_time
@retry_on_failure(max_retries=3, delay=2.0)
def sync_stock_master_from_krx(target_date: date | None = None) -> int:
    from pykrx import stock as krx

    if target_date is None:
        target_date = date.today()

    logger.info(f"Starting stock master sync for {target_date}")

    try:
        date_str = format_krx_date(target_date)
        tickers = krx.get_market_ticker_list(date_str, market="ALL")
        updated_count = 0

        for code in tickers:
            try:
                name = krx.get_market_ticker_name(code)
                try:
                    market = krx.get_stock_market_from_ticker(code)
                except Exception as e:
                    logger.warning(f"Failed to get market for {code}: {e}")
                    market = ""

                Stock.objects.update_or_create(
                    code=code,
                    defaults={
                        "name": name,
                        "market": market,
                        "is_active": True,
                    },
                )
                updated_count += 1
            except Exception as e:
                logger.error(f"Failed to sync stock {code}: {e}")
                continue

        logger.info(f"Successfully synced {updated_count} stocks")
        return updated_count
    except Exception as e:
        logger.error(f"Stock master sync failed: {e}", exc_info=True)
        raise StockDataFetchError(f"Failed to sync stock master: {e}")


@log_execution_time
@retry_on_failure(max_retries=3, delay=2.0)
@transaction.atomic
def sync_daily_prices_from_krx(target_date: date) -> int:
    from pykrx import stock as krx

    logger.info(f"Starting daily price sync for {target_date}")

    try:
        date_str = format_krx_date(target_date)
        df = krx.get_market_ohlcv_by_ticker(date_str, market="ALL")

        if df.empty:
            logger.warning(f"No price data available for {target_date}")
            return 0

        updated_rows = 0

        for code, row in df.iterrows():
            try:
                stock, _ = Stock.objects.get_or_create(code=code, defaults={"name": code})
                open_price = row.get("시가")
                high_price = row.get("고가")
                low_price = row.get("저가")
                close_price = row.get("종가")
                volume = row.get("거래량")
                amount = row.get("거래대금", 0)
                change = row.get("등락", None)
                change_rate = row.get("등락률", None)

                DailyPrice.objects.update_or_create(
                    stock=stock,
                    trade_date=target_date,
                    defaults={
                        "open_price": open_price,
                        "high_price": high_price,
                        "low_price": low_price,
                        "close_price": close_price,
                        "volume": volume,
                        "amount": amount,
                        "change": change,
                        "change_rate": change_rate,
                    },
                )
                updated_rows += 1
            except Exception as e:
                logger.error(f"Failed to sync price for {code}: {e}")
                continue

        logger.info(f"Successfully synced {updated_rows} daily prices")
        return updated_rows
    except Exception as e:
        logger.error(f"Daily price sync failed: {e}", exc_info=True)
        raise StockDataFetchError(f"Failed to sync daily prices: {e}")
