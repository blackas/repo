"""
Celery 태스크 테스트
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from celery.exceptions import Retry

from apps.crypto.tasks import (
    sync_coin_master_task,
    collect_crypto_candles_task,
    recollect_candles_task
)
from apps.crypto.models import Coin, CoinCollectionConfig
from apps.common.exceptions import CryptoDataFetchError


@pytest.mark.django_db
class TestSyncCoinMasterTask:
    def test_sync_coin_master_task_success(self):
        """코인 마스터 동기화 태스크 성공 테스트"""
        with patch('apps.crypto.tasks.fetch_all_coins') as mock_fetch:
            mock_fetch.return_value = 250
            result = sync_coin_master_task()

            assert result["success"] is True
            assert result["count"] == 250
            mock_fetch.assert_called_once()

    def test_sync_coin_master_task_retry_on_fetch_error(self):
        """CryptoDataFetchError 발생 시 재시도 테스트"""
        with patch('apps.crypto.tasks.fetch_all_coins') as mock_fetch:
            mock_fetch.side_effect = CryptoDataFetchError("API error")

            with patch.object(sync_coin_master_task, 'retry', side_effect=Retry("Retry called")) as mock_retry:
                with pytest.raises(Retry):
                    sync_coin_master_task()

                mock_retry.assert_called_once()
                call_args = mock_retry.call_args
                assert isinstance(call_args.kwargs['exc'], CryptoDataFetchError)

    def test_sync_coin_master_task_retry_on_general_exception(self):
        """일반 예외 발생 시 재시도 테스트"""
        with patch('apps.crypto.tasks.fetch_all_coins') as mock_fetch:
            mock_fetch.side_effect = Exception("Unexpected error")

            with patch.object(sync_coin_master_task, 'retry', side_effect=Retry("Retry called")) as mock_retry:
                with pytest.raises(Retry):
                    sync_coin_master_task()

                mock_retry.assert_called_once()
                call_args = mock_retry.call_args
                assert isinstance(call_args.kwargs['exc'], Exception)


@pytest.mark.django_db
class TestCollectCryptoCandlesTask:
    def test_collect_crypto_candles_task_success(self, coin):
        """암호화폐 캔들 수집 태스크 성공 테스트"""
        # 활성화된 설정 생성
        config = CoinCollectionConfig.objects.create(
            name="테스트 설정",
            candle_type="days",
            period_days=7,
            is_active=True
        )
        config.coins.add(coin)

        with patch('apps.crypto.tasks.bulk_collect_candles') as mock_collect:
            mock_collect.return_value = {
                'success_count': 1,
                'fail_count': 0,
                'total': 1
            }

            result = collect_crypto_candles_task()

            assert result["success"] is True
            assert result["configs_count"] == 1
            assert result["total_success"] == 1
            assert result["total_fail"] == 0
            mock_collect.assert_called_once_with(config)

    def test_collect_crypto_candles_task_no_active_configs(self):
        """활성화된 설정이 없을 때 테스트"""
        result = collect_crypto_candles_task()

        assert result["success"] is True
        assert result["configs_count"] == 0
        assert result["total_coins"] == 0

    def test_collect_crypto_candles_task_multiple_configs(self, coin):
        """여러 설정에 대한 수집 테스트"""
        coin2 = Coin.objects.create(
            market_code="KRW-ETH",
            korean_name="이더리움",
            english_name="Ethereum"
        )

        config1 = CoinCollectionConfig.objects.create(
            name="설정1",
            candle_type="days",
            period_days=7,
            is_active=True
        )
        config1.coins.add(coin)

        config2 = CoinCollectionConfig.objects.create(
            name="설정2",
            candle_type="days",
            period_days=30,
            is_active=True
        )
        config2.coins.add(coin2)

        with patch('apps.crypto.tasks.bulk_collect_candles') as mock_collect:
            mock_collect.side_effect = [
                {'success_count': 1, 'fail_count': 0, 'total': 1},
                {'success_count': 1, 'fail_count': 0, 'total': 1}
            ]

            result = collect_crypto_candles_task()

            assert result["success"] is True
            assert result["configs_count"] == 2
            assert result["total_success"] == 2
            assert result["total_fail"] == 0
            assert mock_collect.call_count == 2

    def test_collect_crypto_candles_task_partial_failure(self, coin):
        """일부 설정 수집 실패 테스트"""
        config = CoinCollectionConfig.objects.create(
            name="테스트 설정",
            candle_type="days",
            period_days=7,
            is_active=True
        )
        config.coins.add(coin)

        with patch('apps.crypto.tasks.bulk_collect_candles') as mock_collect:
            mock_collect.side_effect = Exception("API Error")

            result = collect_crypto_candles_task()

            # 예외가 발생해도 태스크는 계속 진행
            assert result["success"] is True
            assert result["configs_count"] == 0  # 실패한 설정은 카운트되지 않음

    def test_collect_crypto_candles_task_retry_on_fetch_error(self):
        """CryptoDataFetchError 발생 시 재시도 테스트"""
        with patch('apps.crypto.models.CoinCollectionConfig.objects.filter') as mock_filter:
            mock_filter.side_effect = CryptoDataFetchError("API error")

            with patch.object(collect_crypto_candles_task, 'retry', side_effect=Retry("Retry called")) as mock_retry:
                with pytest.raises(Retry):
                    collect_crypto_candles_task()

                mock_retry.assert_called_once()


@pytest.mark.django_db
class TestRecollectCandlesTask:
    def test_recollect_candles_task_success(self, coin):
        """캔들 데이터 재수집 태스크 성공 테스트"""
        config = CoinCollectionConfig.objects.create(
            name="재수집 설정",
            candle_type="days",
            period_days=7,
            is_active=True
        )
        config.coins.add(coin)

        start_date = "2024-11-01"
        end_date = "2024-11-30"

        with patch('apps.crypto.tasks.fetch_coin_candles') as mock_fetch:
            mock_fetch.return_value = 30

            result = recollect_candles_task(
                config_id=config.id,
                start_date_str=start_date,
                end_date_str=end_date
            )

            assert result["success"] is True
            assert result["config_name"] == "재수집 설정"
            assert result["success_count"] == 1
            assert result["fail_count"] == 0
            assert result["start_date"] == start_date
            assert result["end_date"] == end_date

            mock_fetch.assert_called_once_with(
                coin=coin,
                start_date=date(2024, 11, 1),
                end_date=date(2024, 11, 30),
                candle_type="days"
            )

    def test_recollect_candles_task_config_not_found(self):
        """존재하지 않는 설정 ID로 재수집 시 테스트"""
        result = recollect_candles_task(
            config_id=99999,
            start_date_str="2024-11-01",
            end_date_str="2024-11-30"
        )

        assert result["success"] is False
        assert "error" in result

    def test_recollect_candles_task_multiple_coins(self, coin):
        """여러 코인에 대한 재수집 테스트"""
        coin2 = Coin.objects.create(
            market_code="KRW-ETH",
            korean_name="이더리움",
            english_name="Ethereum"
        )

        config = CoinCollectionConfig.objects.create(
            name="다중 코인 설정",
            candle_type="days",
            period_days=7,
            is_active=True
        )
        config.coins.add(coin, coin2)

        with patch('apps.crypto.tasks.fetch_coin_candles') as mock_fetch:
            mock_fetch.return_value = 30

            result = recollect_candles_task(
                config_id=config.id,
                start_date_str="2024-11-01",
                end_date_str="2024-11-30"
            )

            assert result["success"] is True
            assert result["success_count"] == 2
            assert result["fail_count"] == 0
            assert mock_fetch.call_count == 2

    def test_recollect_candles_task_partial_failure(self, coin):
        """일부 코인 재수집 실패 테스트"""
        coin2 = Coin.objects.create(
            market_code="KRW-ETH",
            korean_name="이더리움",
            english_name="Ethereum"
        )

        config = CoinCollectionConfig.objects.create(
            name="부분 실패 설정",
            candle_type="days",
            period_days=7,
            is_active=True
        )
        config.coins.add(coin, coin2)

        with patch('apps.crypto.tasks.fetch_coin_candles') as mock_fetch:
            # 첫 번째는 성공, 두 번째는 실패
            mock_fetch.side_effect = [30, Exception("API Error")]

            result = recollect_candles_task(
                config_id=config.id,
                start_date_str="2024-11-01",
                end_date_str="2024-11-30"
            )

            assert result["success"] is True
            assert result["success_count"] == 1
            assert result["fail_count"] == 1

    def test_recollect_candles_task_inactive_coins(self, coin):
        """비활성 코인은 제외 테스트"""
        coin.is_active = False
        coin.save()

        config = CoinCollectionConfig.objects.create(
            name="비활성 코인 설정",
            candle_type="days",
            period_days=7,
            is_active=True
        )
        config.coins.add(coin)

        with patch('apps.crypto.tasks.fetch_coin_candles') as mock_fetch:
            result = recollect_candles_task(
                config_id=config.id,
                start_date_str="2024-11-01",
                end_date_str="2024-11-30"
            )

            assert result["success"] is True
            assert result["success_count"] == 0
            assert result["fail_count"] == 0
            mock_fetch.assert_not_called()

    def test_recollect_candles_task_zero_candles_collected(self, coin):
        """수집된 캔들이 0개일 때 실패로 카운트 테스트"""
        config = CoinCollectionConfig.objects.create(
            name="0개 수집 설정",
            candle_type="days",
            period_days=7,
            is_active=True
        )
        config.coins.add(coin)

        with patch('apps.crypto.tasks.fetch_coin_candles') as mock_fetch:
            # 0개 반환
            mock_fetch.return_value = 0

            result = recollect_candles_task(
                config_id=config.id,
                start_date_str="2024-11-01",
                end_date_str="2024-11-30"
            )

            assert result["success"] is True
            assert result["success_count"] == 0
            assert result["fail_count"] == 1  # 0개 수집은 실패로 카운트
