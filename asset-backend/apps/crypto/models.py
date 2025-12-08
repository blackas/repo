from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.managers import CoinQuerySet, CoinCandleQuerySet


class Coin(models.Model):
    """암호화폐 코인 정보"""
    market_code = models.CharField("마켓 코드", max_length=20, unique=True, help_text="예: KRW-BTC")
    korean_name = models.CharField("한글명", max_length=100)
    english_name = models.CharField("영문명", max_length=100)
    is_active = models.BooleanField("사용 여부", default=True)
    created_at = models.DateTimeField("생성일시", auto_now_add=True)
    updated_at = models.DateTimeField("수정일시", auto_now=True)

    objects = CoinQuerySet.as_manager()

    class Meta:
        db_table = 'crypto_coin'
        verbose_name = '암호화폐 코인'
        verbose_name_plural = '암호화폐 코인 목록'
        ordering = ['market_code']

    def __str__(self):
        return f"{self.market_code} ({self.korean_name})"


class CoinCandle(models.Model):
    """암호화폐 캔들 데이터 (일봉/주봉/월봉)"""

    CANDLE_TYPE_CHOICES = [
        ('days', '일봉'),
        ('weeks', '주봉'),
        ('months', '월봉'),
    ]

    coin = models.ForeignKey(Coin, on_delete=models.CASCADE, related_name='candles', verbose_name="코인")
    candle_type = models.CharField("캔들 타입", max_length=10, choices=CANDLE_TYPE_CHOICES, default='days', db_index=True)
    trade_date = models.DateField("거래일", db_index=True)

    open_price = models.DecimalField("시가", max_digits=20, decimal_places=8)
    high_price = models.DecimalField("고가", max_digits=20, decimal_places=8)
    low_price = models.DecimalField("저가", max_digits=20, decimal_places=8)
    close_price = models.DecimalField("종가", max_digits=20, decimal_places=8)

    volume = models.DecimalField("거래량(코인)", max_digits=20, decimal_places=8)
    candle_acc_trade_volume = models.DecimalField("누적 거래대금(KRW)", max_digits=20, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField("생성일시", auto_now_add=True)
    updated_at = models.DateTimeField("수정일시", auto_now=True)

    objects = CoinCandleQuerySet.as_manager()

    class Meta:
        db_table = 'crypto_coin_candle'
        verbose_name = '암호화폐 캔들'
        verbose_name_plural = '암호화폐 캔들 데이터'
        unique_together = ('coin', 'candle_type', 'trade_date')
        ordering = ['-trade_date']
        indexes = [
            models.Index(fields=['coin', 'candle_type', '-trade_date']),
        ]

    def __str__(self):
        candle_type_display = dict(self.CANDLE_TYPE_CHOICES).get(self.candle_type, self.candle_type)
        return f"{self.coin.market_code} - {self.trade_date} ({candle_type_display})"


class CoinCollectionConfig(models.Model):
    """암호화폐 데이터 수집 설정"""
    name = models.CharField("설정명", max_length=100, unique=True)
    coins = models.ManyToManyField(Coin, related_name='collection_configs', verbose_name="수집 대상 코인")

    CANDLE_TYPE_CHOICES = [
        ('days', '일봉'),
        ('minutes', '분봉'),
        ('weeks', '주봉'),
        ('months', '월봉'),
    ]
    candle_type = models.CharField(
        "캔들 타입",
        max_length=20,
        choices=CANDLE_TYPE_CHOICES,
        default='days',
        help_text="일봉, 분봉, 주봉, 월봉 중 선택"
    )

    INTERVAL_CHOICES = [
        ('daily', '매일'),
        ('weekly', '매주'),
        ('monthly', '매월'),
    ]
    collection_interval = models.CharField(
        "수집 주기",
        max_length=20,
        choices=INTERVAL_CHOICES,
        default='daily',
        help_text="데이터 수집 주기"
    )

    period_days = models.IntegerField(
        "수집 기간(일)",
        default=30,
        help_text="한번에 수집할 일 수 (1~200)",
        validators=[MinValueValidator(1), MaxValueValidator(200)]
    )

    is_active = models.BooleanField("활성화", default=True)
    created_at = models.DateTimeField("생성일시", auto_now_add=True)
    updated_at = models.DateTimeField("수정일시", auto_now=True)

    class Meta:
        db_table = 'crypto_coin_collection_config'
        verbose_name = '암호화폐 수집 설정'
        verbose_name_plural = '암호화폐 수집 설정 목록'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({'활성' if self.is_active else '비활성'})"
