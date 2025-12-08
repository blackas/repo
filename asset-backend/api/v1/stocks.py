from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date
from asgiref.sync import sync_to_async

from api.schemas import (
    StockResponse,
    StockCreate,
    StockUpdate,
    DailyPriceResponse,
    PaginatedResponse,
)
from api.dependencies import get_current_user, get_current_active_superuser
from apps.accounts.models import User
from apps.stocks.models import Stock, DailyPrice, WeeklyPrice, MonthlyPrice, YearlyPrice

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/", response_model=PaginatedResponse[StockResponse])
async def list_stocks(
    page: int = Query(default=1, ge=1, description="페이지 번호 (1부터 시작)"),
    page_size: int = Query(default=20, ge=1, le=100, description="페이지당 아이템 수"),
    market: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    주식 목록 조회 (페이지네이션)
    """
    @sync_to_async
    def get_stocks_paginated():
        queryset = Stock.objects.filter(is_active=True)

        if market:
            queryset = queryset.filter(market=market)

        if search:
            queryset = queryset.filter(name__icontains=search) | queryset.filter(
                code__icontains=search
            )

        total = queryset.count()
        offset = (page - 1) * page_size
        stocks = list(queryset[offset : offset + page_size])

        return stocks, total

    stocks, total = await get_stocks_paginated()
    items = [StockResponse.model_validate(stock) for stock in stocks]

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{stock_code}", response_model=StockResponse)
async def read_stock(
    stock_code: str,
    current_user: User = Depends(get_current_user),
):
    """
    특정 주식 조회
    """
    try:
        stock = await sync_to_async(Stock.objects.get)(code=stock_code, is_active=True)
    except Stock.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found",
        )

    return StockResponse.model_validate(stock)


@router.post("/", response_model=StockResponse, status_code=status.HTTP_201_CREATED)
async def create_stock(
    stock_in: StockCreate,
    current_user: User = Depends(get_current_active_superuser),
):
    """
    주식 생성 (관리자 전용)
    """
    exists = await sync_to_async(Stock.objects.filter(code=stock_in.code).exists)()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock code already exists",
        )

    stock = await sync_to_async(Stock.objects.create)(**stock_in.model_dump())
    return StockResponse.model_validate(stock)


@router.put("/{stock_code}", response_model=StockResponse)
async def update_stock(
    stock_code: str,
    stock_update: StockUpdate,
    current_user: User = Depends(get_current_active_superuser),
):
    """
    주식 정보 수정 (관리자 전용)
    """
    try:
        stock = await sync_to_async(Stock.objects.get)(code=stock_code)
    except Stock.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found",
        )

    update_data = stock_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(stock, field, value)

    await sync_to_async(stock.save)()
    return StockResponse.model_validate(stock)


@router.get("/{stock_code}/prices", response_model=List[DailyPriceResponse])
async def get_stock_prices(
    stock_code: str,
    candle_type: str = Query(default="daily", description="캔들 타입: daily, weekly, monthly, yearly"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(default=30, le=365),
    current_user: User = Depends(get_current_user),
):
    """
    주식 가격 데이터 조회 (다중 시간대 지원)

    candle_type:
    - daily: 일봉 (기본값)
    - weekly: 주봉
    - monthly: 월봉
    - yearly: 연봉
    """
    # candle_type 검증
    valid_candle_types = ["daily", "weekly", "monthly", "yearly"]
    if candle_type not in valid_candle_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid candle_type. Must be one of: {', '.join(valid_candle_types)}",
        )

    try:
        stock = await sync_to_async(Stock.objects.get)(code=stock_code)
    except Stock.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found",
        )

    @sync_to_async
    def get_prices():
        # candle_type에 따라 다른 모델 조회
        if candle_type == "daily":
            queryset = DailyPrice.objects.filter(stock=stock).select_related("stock")
        elif candle_type == "weekly":
            queryset = WeeklyPrice.objects.filter(stock=stock).select_related("stock")
        elif candle_type == "monthly":
            queryset = MonthlyPrice.objects.filter(stock=stock).select_related("stock")
        else:  # yearly
            queryset = YearlyPrice.objects.filter(stock=stock).select_related("stock")

        if start_date:
            queryset = queryset.filter(trade_date__gte=start_date)

        if end_date:
            queryset = queryset.filter(trade_date__lte=end_date)

        return list(queryset[:limit])

    prices = await get_prices()

    result = []
    for price in prices:
        price_dict = DailyPriceResponse.model_validate(price).model_dump()
        price_dict["stock_code"] = stock.code
        price_dict["stock_name"] = stock.name
        result.append(DailyPriceResponse(**price_dict))

    return result
