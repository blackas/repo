import pytest
from datetime import date
from decimal import Decimal

from apps.reports.services import (
    get_watchlist_top_bottom,
    build_daily_report_text,
    create_daily_report_for_user
)
from apps.reports.models import DailyReport
from apps.stocks.models import DailyPrice


@pytest.mark.django_db
class TestGetWatchlistTopBottom:
    def test_get_top_bottom_with_data(self, user, watchlist, stock, daily_price):
        top, bottom = get_watchlist_top_bottom(user, date.today())
        assert len(top) > 0
        assert len(bottom) > 0

    def test_get_top_bottom_empty(self, user):
        top, bottom = get_watchlist_top_bottom(user, date.today())
        assert len(top) == 0
        assert len(bottom) == 0

    def test_get_top_bottom_multiple_stocks(self, user, watchlist, stock):
        from apps.stocks.models import Stock
        from apps.accounts.models import WatchListItem

        stock2 = Stock.objects.create(code="000660", name="SK하이닉스")
        WatchListItem.objects.create(watchlist=watchlist, stock=stock2)

        today = date.today()
        DailyPrice.objects.create(
            stock=stock,
            trade_date=today,
            open_price=Decimal("70000"),
            high_price=Decimal("71000"),
            low_price=Decimal("69000"),
            close_price=Decimal("70500"),
            volume=1000000,
            change_rate=Decimal("2.5")
        )
        DailyPrice.objects.create(
            stock=stock2,
            trade_date=today,
            open_price=Decimal("100000"),
            high_price=Decimal("101000"),
            low_price=Decimal("99000"),
            close_price=Decimal("100500"),
            volume=500000,
            change_rate=Decimal("-1.2")
        )

        top, bottom = get_watchlist_top_bottom(user, today, limit=3)
        assert top[0].stock == stock
        assert bottom[0].stock == stock2


@pytest.mark.django_db
class TestBuildDailyReportText:
    def test_build_report_with_data(self, user, watchlist, stock, daily_price):
        text = build_daily_report_text(user, date.today())
        assert "일일 리포트" in text
        assert "삼성전자" in text
        assert "관심종목" in text

    def test_build_report_no_data(self, user):
        text = build_daily_report_text(user, date.today())
        assert "일일 리포트" in text
        assert "데이터 없음" in text


@pytest.mark.django_db
class TestCreateDailyReportForUser:
    def test_create_daily_report(self, user, watchlist, stock, daily_price):
        report = create_daily_report_for_user(user, date.today())
        assert report.user == user
        assert report.report_date == date.today()
        assert "일일 리포트" in report.body_text

    def test_create_daily_report_update_existing(self, user, daily_report):
        original_text = daily_report.body_text
        report = create_daily_report_for_user(user, date.today())
        assert report.id == daily_report.id
        assert DailyReport.objects.count() == 1
