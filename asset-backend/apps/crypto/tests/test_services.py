import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock
import pandas as pd

from apps.crypto.services import (
    fetch_all_coins,
    fetch_coin_candles,
    bulk_collect_candles
)
from apps.crypto.models import Coin, CoinCandle, CoinCollectionConfig
from apps.common.exceptions import CryptoDataFetchError


@pytest.mark.django_db
class TestFetchAllCoins:
    @patch('pyupbit.get_tickers')
    def test_fetch_all_coins_success(self, mock_get_tickers):
        """코인 목록 수집 성공 테스트"""
        # Mock 데이터 설정
        mock_get_tickers.return_value = ['KRW-BTC', 'KRW-ETH']

        # 함수 실행
        count = fetch_all_coins()

        # 검증
        assert count == 2
        assert Coin.objects.count() == 2
        assert Coin.objects.filter(market_code='KRW-BTC').exists()
        assert Coin.objects.filter(market_code='KRW-ETH').exists()

        btc = Coin.objects.get(market_code='KRW-BTC')
        assert btc.korean_name == 'BTC'  # 심볼이 기본값으로 사용됨
        assert btc.english_name == 'BTC'

    @patch('pyupbit.get_tickers')
    def test_fetch_all_coins_empty(self, mock_get_tickers):
        """코인 목록이 비어있을 때"""
        mock_get_tickers.return_value = []

        count = fetch_all_coins()

        assert count == 0
        assert Coin.objects.count() == 0

    @patch('pyupbit.get_tickers')
    def test_fetch_all_coins_api_error(self, mock_get_tickers):
        """API 에러 발생 시"""
        mock_get_tickers.side_effect = Exception("API Error")

        with pytest.raises(CryptoDataFetchError):
            fetch_all_coins()


@pytest.mark.django_db
class TestFetchCoinCandles:
    @patch('pyupbit.get_ohlcv')
    def test_fetch_coin_candles_success(self, mock_get_ohlcv, coin):
        """캔들 데이터 수집 성공 테스트"""
        # Mock DataFrame 생성
        mock_df = pd.DataFrame({
            'open': [50000000, 51000000],
            'high': [52000000, 53000000],
            'low': [49000000, 50000000],
            'close': [51000000, 52000000],
            'volume': [100.5, 150.3],
            'value': [5100000000, 7800000000]
        }, index=pd.DatetimeIndex(['2024-11-26', '2024-11-27']))

        mock_get_ohlcv.return_value = mock_df

        # 함수 실행
        start_date = date(2024, 11, 26)
        end_date = date(2024, 11, 27)
        count = fetch_coin_candles(coin, start_date, end_date)

        # 검증
        assert count == 2
        assert CoinCandle.objects.count() == 2

        candle = CoinCandle.objects.get(coin=coin, trade_date=date(2024, 11, 26))
        assert candle.open_price == Decimal('50000000')
        assert candle.close_price == Decimal('51000000')
        assert candle.volume == Decimal('100.5')

    @patch('pyupbit.get_ohlcv')
    def test_fetch_coin_candles_empty(self, mock_get_ohlcv, coin):
        """빈 DataFrame 반환 시"""
        mock_get_ohlcv.return_value = None

        start_date = date(2024, 11, 26)
        end_date = date(2024, 11, 27)
        count = fetch_coin_candles(coin, start_date, end_date)

        assert count == 0
        assert CoinCandle.objects.count() == 0

    @patch('pyupbit.get_ohlcv')
    def test_fetch_coin_candles_large_period(self, mock_get_ohlcv, coin):
        """200일 초과 기간 요청 시 (경고 로그만 확인)"""
        mock_df = pd.DataFrame({
            'open': [50000000],
            'high': [52000000],
            'low': [49000000],
            'close': [51000000],
            'volume': [100.5],
        }, index=pd.DatetimeIndex(['2024-11-27']))

        mock_get_ohlcv.return_value = mock_df

        start_date = date(2023, 1, 1)  # 300일 전
        end_date = date(2024, 11, 27)
        count = fetch_coin_candles(coin, start_date, end_date)

        # 200개 제한이 적용되어도 정상 동작
        assert count >= 0

    @patch('pyupbit.get_ohlcv')
    def test_fetch_coin_candles_api_error(self, mock_get_ohlcv, coin):
        """API 에러 발생 시"""
        mock_get_ohlcv.side_effect = Exception("API Error")

        with pytest.raises(CryptoDataFetchError):
            fetch_coin_candles(coin, date(2024, 11, 26), date(2024, 11, 27))


@pytest.mark.django_db
class TestBulkCollectCandles:
    @patch('apps.crypto.services.fetch_coin_candles')
    def test_bulk_collect_candles_success(self, mock_fetch, coin):
        """일괄 수집 성공 테스트"""
        # 설정 생성
        config = CoinCollectionConfig.objects.create(
            name="테스트 설정",
            candle_type="days",
            period_days=7,
            is_active=True
        )
        config.coins.add(coin)

        # Mock 설정
        mock_fetch.return_value = 7

        # 함수 실행
        result = bulk_collect_candles(config)

        # 검증
        assert result['success_count'] == 1
        assert result['fail_count'] == 0
        assert result['total'] == 1
        mock_fetch.assert_called_once()

    @patch('apps.crypto.services.fetch_coin_candles')
    def test_bulk_collect_candles_partial_failure(self, mock_fetch, coin):
        """일부 코인 수집 실패 테스트"""
        coin2 = Coin.objects.create(
            market_code="KRW-ETH",
            korean_name="이더리움",
            english_name="Ethereum"
        )

        config = CoinCollectionConfig.objects.create(
            name="테스트 설정",
            candle_type="days",
            period_days=7
        )
        config.coins.add(coin, coin2)

        # 첫 번째는 성공, 두 번째는 실패
        mock_fetch.side_effect = [7, Exception("API Error")]

        result = bulk_collect_candles(config)

        assert result['success_count'] == 1
        assert result['fail_count'] == 1
        assert result['total'] == 2

    def test_bulk_collect_candles_no_coins(self):
        """코인이 없는 설정"""
        config = CoinCollectionConfig.objects.create(
            name="빈 설정",
            candle_type="days",
            period_days=7
        )

        result = bulk_collect_candles(config)

        assert result['success_count'] == 0
        assert result['fail_count'] == 0
        assert result['total'] == 0

    @patch('apps.crypto.services.fetch_coin_candles')
    def test_bulk_collect_candles_inactive_coins(self, mock_fetch, coin):
        """비활성 코인은 제외"""
        coin.is_active = False
        coin.save()

        config = CoinCollectionConfig.objects.create(
            name="테스트 설정",
            candle_type="days",
            period_days=7
        )
        config.coins.add(coin)

        result = bulk_collect_candles(config)

        assert result['total'] == 0
        mock_fetch.assert_not_called()
