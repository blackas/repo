import pytest
from datetime import date
from decimal import Decimal

from apps.stocks.models import Stock, DailyPrice


@pytest.mark.django_db
class TestStockModel:
    def test_create_stock(self):
        stock = Stock.objects.create(
            code="005930",
            name="삼성전자",
            market="KOSPI",
            sector="전기전자"
        )
        assert stock.code == "005930"
        assert stock.name == "삼성전자"
        assert stock.is_active is True

    def test_stock_string_representation(self, stock):
        assert str(stock) == "005930 삼성전자"

    def test_stock_unique_code(self, stock):
        with pytest.raises(Exception):
            Stock.objects.create(
                code="005930",
                name="중복"
            )


@pytest.mark.django_db
class TestDailyPriceModel:
    def test_create_daily_price(self, stock):
        price = DailyPrice.objects.create(
            stock=stock,
            trade_date=date.today(),
            open_price=Decimal("70000"),
            high_price=Decimal("71000"),
            low_price=Decimal("69000"),
            close_price=Decimal("70500"),
            volume=1000000
        )
        assert price.stock == stock
        assert price.close_price == Decimal("70500")
        assert price.volume == 1000000

    def test_daily_price_unique_constraint(self, stock):
        today = date.today()
        DailyPrice.objects.create(
            stock=stock,
            trade_date=today,
            open_price=Decimal("70000"),
            high_price=Decimal("71000"),
            low_price=Decimal("69000"),
            close_price=Decimal("70500"),
            volume=1000000
        )
        with pytest.raises(Exception):
            DailyPrice.objects.create(
                stock=stock,
                trade_date=today,
                open_price=Decimal("70000"),
                high_price=Decimal("71000"),
                low_price=Decimal("69000"),
                close_price=Decimal("70500"),
                volume=1000000
            )

    def test_daily_price_ordering(self, stock):
        from datetime import timedelta
        today = date.today()
        yesterday = today - timedelta(days=1)

        price_today = DailyPrice.objects.create(
            stock=stock,
            trade_date=today,
            open_price=Decimal("70000"),
            high_price=Decimal("71000"),
            low_price=Decimal("69000"),
            close_price=Decimal("70500"),
            volume=1000000
        )
        price_yesterday = DailyPrice.objects.create(
            stock=stock,
            trade_date=yesterday,
            open_price=Decimal("69000"),
            high_price=Decimal("70000"),
            low_price=Decimal("68000"),
            close_price=Decimal("69500"),
            volume=900000
        )

        prices = list(DailyPrice.objects.all())
        assert prices[0] == price_today
        assert prices[1] == price_yesterday

    def test_daily_price_with_change_rate(self, daily_price):
        assert daily_price.change == Decimal("500")
        assert daily_price.change_rate == Decimal("0.71")
