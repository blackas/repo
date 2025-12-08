import logging
from datetime import date
from django.db import transaction
from django.db.models import Min, Max, Sum, Q, F
from django.db.models.functions import TruncWeek, TruncMonth, TruncYear

from .models import Stock, DailyPrice, WeeklyPrice, MonthlyPrice, YearlyPrice
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


@log_execution_time
@retry_on_failure(max_retries=3, delay=2.0)
@transaction.atomic
def aggregate_weekly_prices(stock: Stock, start_date: date, end_date: date) -> int:
    """
    주봉 캔들 데이터 집계

    일봉 데이터를 주 단위로 그룹화하여 주봉 캔들 생성
    ISO 주차 기준 (월요일 시작, 일요일 종료)
    """
    logger.info(f"Aggregating weekly prices for {stock.code} from {start_date} to {end_date}")

    try:
        # 기간 내 일봉 데이터 조회
        daily_prices = DailyPrice.objects.filter(
            stock=stock,
            trade_date__range=[start_date, end_date]
        ).order_by('trade_date')

        if not daily_prices.exists():
            logger.warning(f"No daily prices found for {stock.code}")
            return 0

        # 주 단위로 그룹화
        weekly_data = {}
        for price in daily_prices:
            # ISO 주차 계산 (년도-주차)
            year, week, _ = price.trade_date.isocalendar()
            week_key = f"{year}-W{week:02d}"

            if week_key not in weekly_data:
                weekly_data[week_key] = {
                    'prices': [],
                    'dates': []
                }

            weekly_data[week_key]['prices'].append(price)
            weekly_data[week_key]['dates'].append(price.trade_date)

        # 주봉 생성
        created_count = 0
        for week_key, data in weekly_data.items():
            prices = data['prices']
            dates = data['dates']

            # 주의 마지막 거래일
            last_date = max(dates)

            # OHLC 계산
            open_price = next(p.open_price for p in prices if p.trade_date == min(dates))
            high_price = max(p.high_price for p in prices)
            low_price = min(p.low_price for p in prices)
            close_price = next(p.close_price for p in prices if p.trade_date == last_date)
            volume = sum(p.volume for p in prices)
            amount = sum(p.amount for p in prices if p.amount) if any(p.amount for p in prices) else None

            WeeklyPrice.objects.update_or_create(
                stock=stock,
                trade_date=last_date,
                defaults={
                    'open_price': open_price,
                    'high_price': high_price,
                    'low_price': low_price,
                    'close_price': close_price,
                    'volume': volume,
                    'amount': amount,
                }
            )
            created_count += 1

        logger.info(f"Successfully aggregated {created_count} weekly prices for {stock.code}")
        return created_count

    except Exception as e:
        logger.error(f"Weekly price aggregation failed for {stock.code}: {e}", exc_info=True)
        raise StockDataFetchError(f"Failed to aggregate weekly prices: {e}")


@log_execution_time
@retry_on_failure(max_retries=3, delay=2.0)
@transaction.atomic
def aggregate_monthly_prices(stock: Stock, start_date: date, end_date: date) -> int:
    """
    월봉 캔들 데이터 집계

    일봉 데이터를 월 단위로 그룹화하여 월봉 캔들 생성
    """
    logger.info(f"Aggregating monthly prices for {stock.code} from {start_date} to {end_date}")

    try:
        # 기간 내 일봉 데이터 조회
        daily_prices = DailyPrice.objects.filter(
            stock=stock,
            trade_date__range=[start_date, end_date]
        ).order_by('trade_date')

        if not daily_prices.exists():
            logger.warning(f"No daily prices found for {stock.code}")
            return 0

        # 월 단위로 그룹화
        monthly_data = {}
        for price in daily_prices:
            month_key = f"{price.trade_date.year}-{price.trade_date.month:02d}"

            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'prices': [],
                    'dates': []
                }

            monthly_data[month_key]['prices'].append(price)
            monthly_data[month_key]['dates'].append(price.trade_date)

        # 월봉 생성
        created_count = 0
        for month_key, data in monthly_data.items():
            prices = data['prices']
            dates = data['dates']

            # 월의 마지막 거래일
            last_date = max(dates)

            # OHLC 계산
            open_price = next(p.open_price for p in prices if p.trade_date == min(dates))
            high_price = max(p.high_price for p in prices)
            low_price = min(p.low_price for p in prices)
            close_price = next(p.close_price for p in prices if p.trade_date == last_date)
            volume = sum(p.volume for p in prices)
            amount = sum(p.amount for p in prices if p.amount) if any(p.amount for p in prices) else None

            MonthlyPrice.objects.update_or_create(
                stock=stock,
                trade_date=last_date,
                defaults={
                    'open_price': open_price,
                    'high_price': high_price,
                    'low_price': low_price,
                    'close_price': close_price,
                    'volume': volume,
                    'amount': amount,
                }
            )
            created_count += 1

        logger.info(f"Successfully aggregated {created_count} monthly prices for {stock.code}")
        return created_count

    except Exception as e:
        logger.error(f"Monthly price aggregation failed for {stock.code}: {e}", exc_info=True)
        raise StockDataFetchError(f"Failed to aggregate monthly prices: {e}")


@log_execution_time
@retry_on_failure(max_retries=3, delay=2.0)
@transaction.atomic
def aggregate_yearly_prices(stock: Stock, start_date: date, end_date: date) -> int:
    """
    연봉 캔들 데이터 집계

    일봉 데이터를 연 단위로 그룹화하여 연봉 캔들 생성
    """
    logger.info(f"Aggregating yearly prices for {stock.code} from {start_date} to {end_date}")

    try:
        # 기간 내 일봉 데이터 조회
        daily_prices = DailyPrice.objects.filter(
            stock=stock,
            trade_date__range=[start_date, end_date]
        ).order_by('trade_date')

        if not daily_prices.exists():
            logger.warning(f"No daily prices found for {stock.code}")
            return 0

        # 연 단위로 그룹화
        yearly_data = {}
        for price in daily_prices:
            year_key = str(price.trade_date.year)

            if year_key not in yearly_data:
                yearly_data[year_key] = {
                    'prices': [],
                    'dates': []
                }

            yearly_data[year_key]['prices'].append(price)
            yearly_data[year_key]['dates'].append(price.trade_date)

        # 연봉 생성
        created_count = 0
        for year_key, data in yearly_data.items():
            prices = data['prices']
            dates = data['dates']

            # 연의 마지막 거래일
            last_date = max(dates)

            # OHLC 계산
            open_price = next(p.open_price for p in prices if p.trade_date == min(dates))
            high_price = max(p.high_price for p in prices)
            low_price = min(p.low_price for p in prices)
            close_price = next(p.close_price for p in prices if p.trade_date == last_date)
            volume = sum(p.volume for p in prices)
            amount = sum(p.amount for p in prices if p.amount) if any(p.amount for p in prices) else None

            YearlyPrice.objects.update_or_create(
                stock=stock,
                trade_date=last_date,
                defaults={
                    'open_price': open_price,
                    'high_price': high_price,
                    'low_price': low_price,
                    'close_price': close_price,
                    'volume': volume,
                    'amount': amount,
                }
            )
            created_count += 1

        logger.info(f"Successfully aggregated {created_count} yearly prices for {stock.code}")
        return created_count

    except Exception as e:
        logger.error(f"Yearly price aggregation failed for {stock.code}: {e}", exc_info=True)
        raise StockDataFetchError(f"Failed to aggregate yearly prices: {e}")
