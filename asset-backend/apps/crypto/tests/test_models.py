import pytest
from datetime import date
from decimal import Decimal
from django.db import IntegrityError

from apps.crypto.models import Coin, CoinCandle, CoinCollectionConfig


@pytest.mark.django_db
class TestCoinModel:
    def test_create_coin(self):
        """코인 생성 테스트"""
        coin = Coin.objects.create(
            market_code="KRW-ETH",
            korean_name="이더리움",
            english_name="Ethereum",
            is_active=True
        )
        assert coin.market_code == "KRW-ETH"
        assert coin.korean_name == "이더리움"
        assert coin.is_active is True

    def test_coin_str(self, coin):
        """코인 __str__ 테스트"""
        assert str(coin) == "KRW-BTC (비트코인)"

    def test_coin_unique_market_code(self, coin):
        """마켓 코드 unique 제약 테스트"""
        with pytest.raises(IntegrityError):
            Coin.objects.create(
                market_code="KRW-BTC",  # 중복
                korean_name="비트코인2",
                english_name="Bitcoin2"
            )

    def test_coin_queryset_active(self, coin):
        """활성 코인 조회 테스트"""
        inactive_coin = Coin.objects.create(
            market_code="KRW-XRP",
            korean_name="리플",
            english_name="Ripple",
            is_active=False
        )

        active_coins = Coin.objects.active()
        assert coin in active_coins
        assert inactive_coin not in active_coins

    def test_coin_queryset_search(self, coin):
        """코인 검색 테스트"""
        results = Coin.objects.search("비트")
        assert coin in results

        results = Coin.objects.search("BTC")
        assert coin in results


@pytest.mark.django_db
class TestCoinCandleModel:
    def test_create_candle(self, coin):
        """캔들 생성 테스트"""
        candle = CoinCandle.objects.create(
            coin=coin,
            trade_date=date.today(),
            open_price=Decimal("50000000.12345678"),
            high_price=Decimal("51000000.00000000"),
            low_price=Decimal("49000000.00000000"),
            close_price=Decimal("50500000.50000000"),
            volume=Decimal("123.45678901"),
            candle_acc_trade_volume=Decimal("6200000000.50")
        )
        assert candle.coin == coin
        assert candle.open_price == Decimal("50000000.12345678")

    def test_candle_str(self, coin):
        """캔들 __str__ 테스트"""
        candle = CoinCandle.objects.create(
            coin=coin,
            trade_date=date(2024, 11, 27),
            open_price=Decimal("50000000"),
            high_price=Decimal("51000000"),
            low_price=Decimal("49000000"),
            close_price=Decimal("50500000"),
            volume=Decimal("123.45678901")
        )
        assert str(candle) == "KRW-BTC - 2024-11-27"

    def test_candle_unique_together(self, coin):
        """coin + trade_date unique 제약 테스트"""
        CoinCandle.objects.create(
            coin=coin,
            trade_date=date.today(),
            open_price=Decimal("50000000"),
            high_price=Decimal("51000000"),
            low_price=Decimal("49000000"),
            close_price=Decimal("50500000"),
            volume=Decimal("123.45678901")
        )

        with pytest.raises(IntegrityError):
            CoinCandle.objects.create(
                coin=coin,
                trade_date=date.today(),  # 같은 날짜
                open_price=Decimal("50000000"),
                high_price=Decimal("51000000"),
                low_price=Decimal("49000000"),
                close_price=Decimal("50500000"),
                volume=Decimal("123.45678901")
            )

    def test_candle_queryset_for_coin(self, coin):
        """특정 코인의 캔들 조회 테스트"""
        candle1 = CoinCandle.objects.create(
            coin=coin,
            trade_date=date(2024, 11, 27),
            open_price=Decimal("50000000"),
            high_price=Decimal("51000000"),
            low_price=Decimal("49000000"),
            close_price=Decimal("50500000"),
            volume=Decimal("123.45678901")
        )

        # 다른 코인의 캔들
        other_coin = Coin.objects.create(
            market_code="KRW-ETH",
            korean_name="이더리움",
            english_name="Ethereum"
        )
        CoinCandle.objects.create(
            coin=other_coin,
            trade_date=date(2024, 11, 27),
            open_price=Decimal("3000000"),
            high_price=Decimal("3100000"),
            low_price=Decimal("2900000"),
            close_price=Decimal("3050000"),
            volume=Decimal("1000.123456")
        )

        candles = CoinCandle.objects.for_coin(coin)
        assert candle1 in candles
        assert candles.count() == 1


@pytest.mark.django_db
class TestCoinCollectionConfigModel:
    def test_create_config(self, coin):
        """수집 설정 생성 테스트"""
        config = CoinCollectionConfig.objects.create(
            name="비트코인 일봉 수집",
            candle_type="days",
            collection_interval="daily",
            period_days=30,
            is_active=True
        )
        config.coins.add(coin)

        assert config.name == "비트코인 일봉 수집"
        assert config.is_active is True
        assert config.coins.count() == 1

    def test_config_str(self, coin):
        """설정 __str__ 테스트"""
        config = CoinCollectionConfig.objects.create(
            name="테스트 설정",
            is_active=True
        )
        assert str(config) == "테스트 설정 (활성)"

        config.is_active = False
        config.save()
        assert str(config) == "테스트 설정 (비활성)"

    def test_config_period_days_validation(self):
        """period_days 유효성 검사 테스트"""
        from django.core.exceptions import ValidationError

        # 1~200 범위 내
        config = CoinCollectionConfig(
            name="테스트",
            period_days=100
        )
        config.full_clean()  # 검증 통과

        # 0은 실패
        config = CoinCollectionConfig(
            name="테스트2",
            period_days=0
        )
        with pytest.raises(ValidationError):
            config.full_clean()

        # 201은 실패
        config = CoinCollectionConfig(
            name="테스트3",
            period_days=201
        )
        with pytest.raises(ValidationError):
            config.full_clean()

    def test_config_m2m_coins(self, coin):
        """M2M 관계 테스트"""
        coin2 = Coin.objects.create(
            market_code="KRW-ETH",
            korean_name="이더리움",
            english_name="Ethereum"
        )

        config = CoinCollectionConfig.objects.create(
            name="다중 코인 수집"
        )
        config.coins.add(coin, coin2)

        assert config.coins.count() == 2
        assert coin in config.coins.all()
        assert coin2 in config.coins.all()
