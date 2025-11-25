from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date
from asgiref.sync import sync_to_async

from api.schemas import (
    StockResponse,
    StockCreate,
    StockUpdate,
    DailyPriceResponse,
)
from api.dependencies import get_current_user, get_current_active_superuser
from apps.accounts.models import User
from apps.stocks.models import Stock, DailyPrice

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/", response_model=List[StockResponse])
async def list_stocks(
    skip: int = 0,
    limit: int = 100,
    market: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    주식 목록 조회
    """
    @sync_to_async
    def get_stocks():
        queryset = Stock.objects.filter(is_active=True)

        if market:
            queryset = queryset.filter(market=market)

        if search:
            queryset = queryset.filter(name__icontains=search) | queryset.filter(
                code__icontains=search
            )

        return list(queryset[skip : skip + limit])

    stocks = await get_stocks()
    return [StockResponse.model_validate(stock) for stock in stocks]


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
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(default=30, le=365),
    current_user: User = Depends(get_current_user),
):
    """
    주식 가격 데이터 조회
    """
    try:
        stock = await sync_to_async(Stock.objects.get)(code=stock_code)
    except Stock.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found",
        )

    @sync_to_async
    def get_prices():
        queryset = DailyPrice.objects.filter(stock=stock).select_related("stock")

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
