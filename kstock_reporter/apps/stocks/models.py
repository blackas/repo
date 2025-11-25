from django.db import models

class Stock(models.Model):
    code = models.CharField("종목코드", max_length=10, unique=True)
    name = models.CharField("종목명", max_length=100)
    market = models.CharField("시장", max_length=20, blank=True, null=True)
    sector = models.CharField("섹터", max_length=100, blank=True, null=True)
    listed_at = models.DateField("상장일", blank=True, null=True)
    is_active = models.BooleanField("사용 여부", default=True)

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

    class Meta:
        unique_together = ("stock", "trade_date")
        ordering = ["-trade_date"]
