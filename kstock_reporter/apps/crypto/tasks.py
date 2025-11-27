"""
암호화폐 데이터 수집 Celery 태스크

Upbit API를 통해 암호화폐 코인 마스터 데이터와 일별 캔들 데이터를 동기화합니다.
"""
import logging
from datetime import date
from celery import shared_task

from .services import fetch_all_coins, bulk_collect_candles, fetch_coin_candles
from .models import CoinCollectionConfig, Coin
from apps.common.exceptions import CryptoDataFetchError

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_coin_master_task(self):
    """
    암호화폐 코인 마스터 데이터 동기화 태스크

    Upbit의 모든 KRW 마켓 코인 목록을 조회하여 데이터베이스에 동기화합니다.

    Returns:
        dict: 성공 여부와 동기화된 코인 수

    Raises:
        Retry: CryptoDataFetchError 발생 시 재시도
    """
    try:
        logger.info("[Task] Starting coin master sync from Upbit")
        count = fetch_all_coins()
        logger.info(f"[Task] Completed coin master sync: {count} coins")
        return {"success": True, "count": count}

    except CryptoDataFetchError as exc:
        logger.error(f"[Task] Coin master sync failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)
    except Exception as exc:
        logger.error(f"[Task] Unexpected error in coin master sync: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def collect_crypto_candles_task(self):
    """
    활성화된 모든 수집 설정에 따라 암호화폐 캔들 데이터 수집

    CoinCollectionConfig에서 is_active=True인 모든 설정을 조회하여
    각 설정에 정의된 코인들의 캔들 데이터를 수집합니다.

    Returns:
        dict: 수집 결과 통계

    Raises:
        Retry: CryptoDataFetchError 발생 시 재시도
    """
    try:
        logger.info("[Task] Starting crypto candles collection")

        active_configs = CoinCollectionConfig.objects.filter(is_active=True)

        if not active_configs.exists():
            logger.warning("[Task] No active collection configs found")
            return {"success": True, "configs_count": 0, "total_coins": 0}

        total_success = 0
        total_fail = 0
        configs_count = 0

        for config in active_configs:
            try:
                result = bulk_collect_candles(config)
                total_success += result['success_count']
                total_fail += result['fail_count']
                configs_count += 1
                logger.info(
                    f"[Task] Config '{config.name}': "
                    f"{result['success_count']} success, {result['fail_count']} failed"
                )
            except Exception as e:
                logger.error(f"[Task] Failed to process config '{config.name}': {e}")
                continue

        logger.info(
            f"[Task] Completed crypto candles collection: "
            f"{configs_count} configs, {total_success} success, {total_fail} failed"
        )

        return {
            "success": True,
            "configs_count": configs_count,
            "total_success": total_success,
            "total_fail": total_fail
        }

    except CryptoDataFetchError as exc:
        logger.error(f"[Task] Crypto candles collection failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)
    except Exception as exc:
        logger.error(f"[Task] Unexpected error in crypto candles collection: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def recollect_candles_task(self, config_id: int, start_date_str: str, end_date_str: str):
    """
    특정 설정에 대한 캔들 데이터 재수집 태스크

    Django Admin의 재수집 액션에서 호출되며, 특정 기간의 캔들 데이터를 재수집합니다.

    Args:
        config_id: CoinCollectionConfig ID
        start_date_str: 시작일 (YYYY-MM-DD 형식)
        end_date_str: 종료일 (YYYY-MM-DD 형식)

    Returns:
        dict: 재수집 결과

    Raises:
        Retry: CryptoDataFetchError 발생 시 재시도
    """
    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)

        config = CoinCollectionConfig.objects.get(id=config_id)

        logger.info(
            f"[Task] Starting recollection for config '{config.name}' "
            f"from {start_date} to {end_date}"
        )

        coins = config.coins.filter(is_active=True)
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
                    logger.info(f"[Task] Recollected {count} candles for {coin.market_code}")
                else:
                    fail_count += 1
                    logger.warning(f"[Task] No candles collected for {coin.market_code}")

            except Exception as e:
                logger.error(f"[Task] Failed to recollect for {coin.market_code}: {e}")
                fail_count += 1
                continue

        logger.info(
            f"[Task] Completed recollection for '{config.name}': "
            f"{success_count} success, {fail_count} failed"
        )

        return {
            "success": True,
            "config_name": config.name,
            "success_count": success_count,
            "fail_count": fail_count,
            "start_date": start_date_str,
            "end_date": end_date_str
        }

    except CoinCollectionConfig.DoesNotExist:
        logger.error(f"[Task] Config with id {config_id} does not exist")
        return {"success": False, "error": "Config not found"}
    except CryptoDataFetchError as exc:
        logger.error(f"[Task] Recollection failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)
    except Exception as exc:
        logger.error(f"[Task] Unexpected error in recollection: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=60)
