import logging
import time
from datetime import date, timedelta
from decimal import Decimal
from django.db import transaction
import pyupbit
import pandas as pd

from apps.common.exceptions import CryptoDataFetchError
from apps.common.utils import log_execution_time, retry_on_failure
from .models import Coin, CoinCandle

logger = logging.getLogger(__name__)


@log_execution_time
@retry_on_failure(max_retries=3, delay=2.0)
def fetch_all_coins() -> int:
    """
    Upbit의 모든 KRW 마켓 코인 목록 조회 및 DB 저장

    Returns:
        int: 업데이트된 코인 수
    """
    try:
        logger.info("Starting to fetch all KRW market coins from Upbit")

        # KRW 마켓의 모든 티커 조회
        tickers = pyupbit.get_tickers(fiat="KRW")
        time.sleep(0.15)  # Rate limiting: ~6.7 req/sec

        if not tickers:
            logger.warning("No tickers received from Upbit")
            return 0

        updated_count = 0

        with transaction.atomic():
            for ticker in tickers:
                # 티커에서 코인 심볼 추출 (예: KRW-BTC -> BTC)
                coin_symbol = ticker.split('-')[-1] if '-' in ticker else ticker

                # 코인 정보 업데이트 또는 생성
                coin, created = Coin.objects.update_or_create(
                    market_code=ticker,
                    defaults={
                        'korean_name': coin_symbol,  # 심볼을 기본값으로 사용
                        'english_name': coin_symbol,
                        'is_active': True
                    }
                )

                if created:
                    logger.debug(f"Created new coin: {ticker}")
                else:
                    logger.debug(f"Updated coin: {ticker}")

                updated_count += 1

                # Rate limiting between tickers
                if updated_count % 10 == 0:
                    time.sleep(0.15)

        logger.info(f"Successfully updated {updated_count} coins")
        return updated_count

    except Exception as e:
        logger.error(f"Error fetching coins from Upbit: {e}", exc_info=True)
        raise CryptoDataFetchError(f"Failed to fetch coins: {e}")


@log_execution_time
@retry_on_failure(max_retries=3, delay=2.0)
def fetch_coin_candles(
    coin: Coin,
    start_date: date,
    end_date: date,
    candle_type: str = "days"
) -> int:
    """
    특정 코인의 캔들 데이터 수집

    Args:
        coin: Coin 모델 인스턴스
        start_date: 수집 시작일
        end_date: 수집 종료일
        candle_type: 캔들 타입 (days, minutes, weeks, months)

    Returns:
        int: 저장된 캔들 수
    """
    try:
        logger.info(
            f"Fetching candles for {coin.market_code} "
            f"from {start_date} to {end_date} ({candle_type})"
        )

        # pyupbit는 최대 200개까지만 조회 가능
        # count 계산
        days_diff = (end_date - start_date).days + 1
        if days_diff > 200:
            logger.warning(
                f"Requested {days_diff} days but pyupbit supports max 200. "
                f"Will fetch only 200 days."
            )

        count = min(days_diff, 200)

        # OHLCV 데이터 조회
        df = pyupbit.get_ohlcv(
            ticker=coin.market_code,
            interval=candle_type,
            count=count,
            to=end_date.strftime('%Y%m%d')  # pyupbit expects YYYYMMDD format
        )
        time.sleep(0.15)  # Rate limiting

        if df is None or df.empty:
            logger.warning(f"No candle data received for {coin.market_code}")
            return 0

        saved_count = 0

        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    # 안전한 날짜 변환
                    if hasattr(index, 'date'):
                        trade_date = index.date()
                    else:
                        trade_date = pd.to_datetime(index).date()

                    # 캔들 데이터 저장
                    candle, created = CoinCandle.objects.update_or_create(
                        coin=coin,
                        trade_date=trade_date,
                        defaults={
                            'open_price': Decimal(str(row['open'])),
                            'high_price': Decimal(str(row['high'])),
                            'low_price': Decimal(str(row['low'])),
                            'close_price': Decimal(str(row['close'])),
                            'volume': Decimal(str(row['volume'])),
                            'candle_acc_trade_volume': Decimal(str(row.get('value', 0)))
                                if 'value' in row else None
                        }
                    )

                    if created:
                        logger.debug(f"Created candle: {coin.market_code} - {trade_date}")
                    else:
                        logger.debug(f"Updated candle: {coin.market_code} - {trade_date}")

                    saved_count += 1

                except Exception as e:
                    logger.error(
                        f"Error saving candle for {coin.market_code} "
                        f"on {trade_date}: {e}"
                    )
                    continue

        logger.info(
            f"Successfully saved {saved_count} candles "
            f"for {coin.market_code}"
        )
        return saved_count

    except Exception as e:
        logger.error(
            f"Error fetching candles for {coin.market_code}: {e}",
            exc_info=True
        )
        raise CryptoDataFetchError(
            f"Failed to fetch candles for {coin.market_code}: {e}"
        )


@log_execution_time
def bulk_collect_candles(config) -> dict:
    """
    CoinCollectionConfig 기반 일괄 캔들 수집

    Args:
        config: CoinCollectionConfig 인스턴스

    Returns:
        dict: 수집 결과 {'success_count': int, 'fail_count': int, 'total': int}
    """
    try:
        logger.info(f"Starting bulk collection for config: {config.name}")

        coins = config.coins.filter(is_active=True)

        if not coins.exists():
            logger.warning(f"No active coins in config: {config.name}")
            return {'success_count': 0, 'fail_count': 0, 'total': 0}

        end_date = date.today()
        start_date = end_date - timedelta(days=config.period_days - 1)

        success_count = 0
        fail_count = 0

        for coin in coins:
            try:
                count = fetch_coin_candles(
                    coin=coin,
                    start_date=start_date,
                    end_date=end_date,
                    candle_type=config.candle_type
                )

                if count > 0:
                    success_count += 1
                else:
                    fail_count += 1

                # Rate limiting between coins
                time.sleep(0.15)

            except Exception as e:
                logger.error(f"Failed to collect candles for {coin.market_code}: {e}")
                fail_count += 1
                continue

        total = success_count + fail_count

        logger.info(
            f"Bulk collection completed for {config.name}: "
            f"{success_count} success, {fail_count} failed, {total} total"
        )

        return {
            'success_count': success_count,
            'fail_count': fail_count,
            'total': total
        }

    except Exception as e:
        logger.error(f"Error in bulk collection for {config.name}: {e}", exc_info=True)
        raise CryptoDataFetchError(f"Failed bulk collection: {e}")
