"""
API 테스트용 pytest fixtures

FastAPI 테스트를 위한 비동기 fixtures를 제공합니다.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from main import app

User = get_user_model()


@pytest_asyncio.fixture
async def async_client():
    """비동기 HTTP 클라이언트"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def api_user(db):
    """API 테스트용 사용자"""
    return User.objects.create_user(
        username="apiuser",
        email="apiuser@test.com",
        password="testpass123",
        phone_number="010-1111-2222",
        receive_daily_report=True
    )


@pytest_asyncio.fixture
async def authenticated_client(async_client: AsyncClient, api_user):
    """인증된 비동기 클라이언트"""
    # 로그인하여 JWT 토큰 획득
    login_data = {
        "username": api_user.username,
        "password": "testpass123"
    }
    response = await async_client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["access_token"]

    # 헤더에 토큰 추가
    async_client.headers.update({"Authorization": f"Bearer {token}"})
    yield async_client


@pytest.fixture
def api_stock(db):
    """API 테스트용 주식 데이터"""
    from apps.stocks.models import Stock
    return Stock.objects.create(
        code="005930",
        name="삼성전자",
        market="KOSPI",
        sector="전기전자",
        is_active=True
    )


@pytest.fixture
def api_daily_price(db, api_stock):
    """API 테스트용 일일 주가 데이터"""
    from apps.stocks.models import DailyPrice
    return DailyPrice.objects.create(
        stock=api_stock,
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
def api_watchlist(db, api_user):
    """API 테스트용 관심목록"""
    from apps.accounts.models import WatchList
    return WatchList.objects.create(
        user=api_user,
        name="API 테스트 관심목록"
    )


@pytest.fixture
def api_watchlist_item(db, api_watchlist, api_stock):
    """API 테스트용 관심목록 아이템"""
    from apps.accounts.models import WatchListItem
    return WatchListItem.objects.create(
        watchlist=api_watchlist,
        stock=api_stock
    )


@pytest.fixture
def api_daily_report(db, api_user):
    """API 테스트용 일일 리포트"""
    from apps.reports.models import DailyReport
    return DailyReport.objects.create(
        user=api_user,
        report_date=date.today(),
        title=f"{date.today()} 주식 리포트",
        body_text="API 테스트 리포트 내용"
    )
