"""
주식 API 테스트

주식 CRUD 및 가격 조회 엔드포인트를 테스트합니다.
"""
import pytest
from httpx import AsyncClient
from datetime import date, timedelta
from decimal import Decimal

from apps.stocks.models import Stock, DailyPrice


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_list_stocks(authenticated_client: AsyncClient, api_stock):
    """주식 목록 조회 테스트"""
    response = await authenticated_client.get("/api/v1/stocks/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["code"] == api_stock.code
    assert data[0]["name"] == api_stock.name


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_list_stocks_with_search(authenticated_client: AsyncClient, api_stock):
    """주식 검색 기능 테스트"""
    # 이름으로 검색
    response = await authenticated_client.get(
        "/api/v1/stocks/",
        params={"search": api_stock.name[:2]}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert api_stock.code in [stock["code"] for stock in data]


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_list_stocks_with_market_filter(authenticated_client: AsyncClient, api_stock):
    """시장별 필터링 테스트"""
    response = await authenticated_client.get(
        "/api/v1/stocks/",
        params={"market": api_stock.market}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(stock["market"] == api_stock.market for stock in data)


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_stock_detail(authenticated_client: AsyncClient, api_stock):
    """주식 상세 조회 테스트"""
    response = await authenticated_client.get(f"/api/v1/stocks/{api_stock.code}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == api_stock.code
    assert data["name"] == api_stock.name
    assert data["market"] == api_stock.market
    assert data["sector"] == api_stock.sector
    assert data["is_active"] == api_stock.is_active


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_stock_not_found(authenticated_client: AsyncClient):
    """존재하지 않는 주식 조회 테스트"""
    response = await authenticated_client.get("/api/v1/stocks/999999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_stock_prices(authenticated_client: AsyncClient, api_stock, api_daily_price):
    """주식 가격 데이터 조회 테스트"""
    response = await authenticated_client.get(f"/api/v1/stocks/{api_stock.code}/prices")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # 가격 데이터 검증
    price_data = data[0]
    assert "stock_code" in price_data
    assert "stock_name" in price_data
    assert price_data["stock_code"] == api_stock.code
    assert price_data["stock_name"] == api_stock.name


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_stock_prices_with_date_range(
    authenticated_client: AsyncClient, api_stock, api_daily_price
):
    """날짜 범위를 지정한 가격 조회 테스트"""
    from asgiref.sync import sync_to_async

    # 과거 가격 데이터 추가
    yesterday = date.today() - timedelta(days=1)
    await sync_to_async(DailyPrice.objects.create)(
        stock=api_stock,
        trade_date=yesterday,
        open_price=Decimal("69000"),
        high_price=Decimal("70000"),
        low_price=Decimal("68000"),
        close_price=Decimal("69500"),
        volume=900000,
        amount=69500000000,
        change=Decimal("-500"),
        change_rate=Decimal("-0.71")
    )

    response = await authenticated_client.get(
        f"/api/v1/stocks/{api_stock.code}/prices",
        params={
            "start_date": yesterday.isoformat(),
            "end_date": date.today().isoformat()
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_stock_prices_not_found(authenticated_client: AsyncClient):
    """존재하지 않는 주식의 가격 조회 테스트"""
    response = await authenticated_client.get("/api/v1/stocks/999999/prices")

    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_list_stocks_unauthenticated(async_client: AsyncClient, api_stock):
    """인증되지 않은 사용자의 주식 목록 조회 테스트"""
    response = await async_client.get("/api/v1/stocks/")

    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_stock_detail_unauthenticated(async_client: AsyncClient, api_stock):
    """인증되지 않은 사용자의 주식 상세 조회 테스트"""
    response = await async_client.get(f"/api/v1/stocks/{api_stock.code}")

    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_pagination_with_skip_limit(authenticated_client: AsyncClient, api_stock):
    """페이지네이션 (skip/limit) 테스트"""
    from asgiref.sync import sync_to_async

    # 추가 주식 데이터 생성
    await sync_to_async(Stock.objects.create)(
        code="000660",
        name="SK하이닉스",
        market="KOSPI",
        sector="전기전자",
        is_active=True
    )

    await sync_to_async(Stock.objects.create)(
        code="035420",
        name="NAVER",
        market="KOSPI",
        sector="IT",
        is_active=True
    )

    # skip=0, limit=2로 조회
    response = await authenticated_client.get(
        "/api/v1/stocks/",
        params={"skip": 0, "limit": 2}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2

    # skip=1, limit=2로 조회
    response = await authenticated_client.get(
        "/api/v1/stocks/",
        params={"skip": 1, "limit": 2}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2
