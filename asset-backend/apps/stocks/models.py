from django.db import models

from apps.common.managers import (
    StockQuerySet,
    DailyPriceQuerySet,
    WeeklyPriceQuerySet,
    MonthlyPriceQuerySet,
    YearlyPriceQuerySet,
)


class Stock(models.Model):
    code = models.CharField("종목코드", max_length=10, unique=True)
    name = models.CharField("종목명", max_length=100)
    market = models.CharField("시장", max_length=20, blank=True, null=True)
    sector = models.CharField("섹터", max_length=100, blank=True, null=True)
    listed_at = models.DateField("상장일", blank=True, null=True)
    is_active = models.BooleanField("사용 여부", default=True)

    objects = StockQuerySet.as_manager()

    def __str__(self):
        return f"{self.code} {self.name}"


class DailyPrice(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="prices")
    trade_date = models.DateField("거래일", db_index=True)
    open_price = models.DecimalField(max_digits=15, decimal_places=2)
    high_price = models.DecimalField(max_digits=15, decimal_places=2)
    low_price = models.DecimalField(max_digits=15, decimal_places=2)
    close_price = models.DecimalField(max_digits=15, decimal_places=2)
    volume = models.BigIntegerField("거래량")
    amount = models.BigIntegerField("거래대금", null=True, blank=True)

    change = models.DecimalField("전일 대비", max_digits=15, decimal_places=2, null=True, blank=True)
    change_rate = models.DecimalField("등락률(%)", max_digits=7, decimal_places=2, null=True, blank=True)
    market_cap = models.BigIntegerField("시가총액", null=True, blank=True)

    objects = DailyPriceQuerySet.as_manager()

    class Meta:
        unique_together = ("stock", "trade_date")
        ordering = ["-trade_date"]


class WeeklyPrice(models.Model):
    """주봉 캔들 데이터"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="weekly_prices")
    trade_date = models.DateField("거래일(주의 마지막 거래일)", db_index=True)
    open_price = models.DecimalField(max_digits=15, decimal_places=2)
    high_price = models.DecimalField(max_digits=15, decimal_places=2)
    low_price = models.DecimalField(max_digits=15, decimal_places=2)
    close_price = models.DecimalField(max_digits=15, decimal_places=2)
    volume = models.BigIntegerField("거래량")
    amount = models.BigIntegerField("거래대금", null=True, blank=True)

    change = models.DecimalField("전주 대비", max_digits=15, decimal_places=2, null=True, blank=True)
    change_rate = models.DecimalField("등락률(%)", max_digits=7, decimal_places=2, null=True, blank=True)
    market_cap = models.BigIntegerField("시가총액", null=True, blank=True)

    objects = WeeklyPriceQuerySet.as_manager()

    class Meta:
        unique_together = ("stock", "trade_date")
        ordering = ["-trade_date"]
        indexes = [
            models.Index(fields=["stock", "-trade_date"]),
        ]

    def __str__(self):
        return f"{self.stock.code} - {self.trade_date} (주봉)"


class MonthlyPrice(models.Model):
    """월봉 캔들 데이터"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="monthly_prices")
    trade_date = models.DateField("거래일(월의 마지막 거래일)", db_index=True)
    open_price = models.DecimalField(max_digits=15, decimal_places=2)
    high_price = models.DecimalField(max_digits=15, decimal_places=2)
    low_price = models.DecimalField(max_digits=15, decimal_places=2)
    close_price = models.DecimalField(max_digits=15, decimal_places=2)
    volume = models.BigIntegerField("거래량")
    amount = models.BigIntegerField("거래대금", null=True, blank=True)

    change = models.DecimalField("전월 대비", max_digits=15, decimal_places=2, null=True, blank=True)
    change_rate = models.DecimalField("등락률(%)", max_digits=7, decimal_places=2, null=True, blank=True)
    market_cap = models.BigIntegerField("시가총액", null=True, blank=True)

    objects = MonthlyPriceQuerySet.as_manager()

    class Meta:
        unique_together = ("stock", "trade_date")
        ordering = ["-trade_date"]
        indexes = [
            models.Index(fields=["stock", "-trade_date"]),
        ]

    def __str__(self):
        return f"{self.stock.code} - {self.trade_date} (월봉)"


class YearlyPrice(models.Model):
    """연봉 캔들 데이터"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="yearly_prices")
    trade_date = models.DateField("거래일(연의 마지막 거래일)", db_index=True)
    open_price = models.DecimalField(max_digits=15, decimal_places=2)
    high_price = models.DecimalField(max_digits=15, decimal_places=2)
    low_price = models.DecimalField(max_digits=15, decimal_places=2)
    close_price = models.DecimalField(max_digits=15, decimal_places=2)
    volume = models.BigIntegerField("거래량")
    amount = models.BigIntegerField("거래대금", null=True, blank=True)

    change = models.DecimalField("전년 대비", max_digits=15, decimal_places=2, null=True, blank=True)
    change_rate = models.DecimalField("등락률(%)", max_digits=7, decimal_places=2, null=True, blank=True)
    market_cap = models.BigIntegerField("시가총액", null=True, blank=True)

    objects = YearlyPriceQuerySet.as_manager()

    class Meta:
        unique_together = ("stock", "trade_date")
        ordering = ["-trade_date"]
        indexes = [
            models.Index(fields=["stock", "-trade_date"]),
        ]

    def __str__(self):
        return f"{self.stock.code} - {self.trade_date} (연봉)"
