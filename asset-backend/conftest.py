import pytest
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    """기본 테스트 사용자"""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        phone_number="010-1234-5678",
        receive_daily_report=True
    )


@pytest.fixture
def admin_user(db):
    """관리자 사용자"""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="admin123"
    )


@pytest.fixture
def stock(db):
    """테스트 주식 데이터"""
    from apps.stocks.models import Stock
    return Stock.objects.create(
        code="005930",
        name="삼성전자",
        market="KOSPI",
        sector="전기전자",
        is_active=True
    )


@pytest.fixture
def daily_price(db, stock):
    """테스트 일일 주가 데이터"""
    from apps.stocks.models import DailyPrice
    return DailyPrice.objects.create(
        stock=stock,
        trade_date=date.today(),
        open_price=Decimal("70000"),
        high_price=Decimal("71000"),
        low_price=Decimal("69000"),
        close_price=Decimal("70500"),
        volume=1000000,
        amount=70500000000,
        change=Decimal("500"),
        change_rate=Decimal("0.71")
    )


@pytest.fixture
def watchlist(db, user):
    """테스트 관심목록"""
    from apps.accounts.models import WatchList
    return WatchList.objects.create(
        user=user,
        name="내 관심목록"
    )


@pytest.fixture
def watchlist_item(db, watchlist, stock):
    """테스트 관심목록 아이템"""
    from apps.accounts.models import WatchListItem
    return WatchListItem.objects.create(
        watchlist=watchlist,
        stock=stock
    )


@pytest.fixture
def daily_report(db, user):
    """테스트 일일 리포트"""
    from apps.reports.models import DailyReport
    return DailyReport.objects.create(
        user=user,
        report_date=date.today(),
        title=f"{date.today()} 주식 리포트",
        body_text="테스트 리포트 내용"
    )


@pytest.fixture
def notification_log(db, user):
    """테스트 알림 로그"""
    from apps.notifications.models import NotificationLog
    return NotificationLog.objects.create(
        user=user,
        channel="kakao",
        message="테스트 메시지",
        success=True,
        response_code="200"
    )

@pytest.fixture
def coin(db):
    from apps.crypto.models import Coin
    return Coin.objects.create(
        market_code="KRW-BTC",
        korean_name="비트코인",
        english_name="Bitcoin",
        is_active=True
    )
