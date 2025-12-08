"""
암호화폐 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date
from asgiref.sync import sync_to_async

from api.schemas import CoinResponse, CoinCandleResponse, PaginatedResponse
from api.dependencies import get_current_user
from apps.accounts.models import User
from apps.crypto.models import Coin, CoinCandle

router = APIRouter(prefix="/crypto", tags=["crypto"])


@router.get("/", response_model=PaginatedResponse[CoinResponse])
async def list_coins(
    page: int = Query(default=1, ge=1, description="페이지 번호 (1부터 시작)"),
    page_size: int = Query(default=20, ge=1, le=100, description="페이지당 아이템 수"),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    암호화폐 코인 목록 조회 (페이지네이션)
    """
    @sync_to_async
    def get_coins_paginated():
        queryset = Coin.objects.filter(is_active=True)

        if search:
            queryset = queryset.search(search)

        total = queryset.count()
        offset = (page - 1) * page_size
        coins = list(queryset[offset : offset + page_size])

        return coins, total

    coins, total = await get_coins_paginated()
    items = [CoinResponse.model_validate(coin) for coin in coins]

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{market_code}", response_model=CoinResponse)
async def read_coin(
    market_code: str,
    current_user: User = Depends(get_current_user),
):
    """
    특정 코인 조회
    """
    try:
        coin = await sync_to_async(Coin.objects.get)(market_code=market_code, is_active=True)
    except Coin.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coin not found",
        )

    return CoinResponse.model_validate(coin)


@router.get("/{market_code}/candles", response_model=List[CoinCandleResponse])
async def get_coin_candles(
    market_code: str,
    candle_type: str = Query(default="days", description="캔들 타입: days, weeks, months"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(default=30, le=200),
    current_user: User = Depends(get_current_user),
):
    """
    코인 캔들 데이터 조회 (다중 시간대 지원)

    candle_type:
    - days: 일봉 (기본값)
    - weeks: 주봉
    - months: 월봉
    """
    # candle_type 검증
    valid_candle_types = ["days", "weeks", "months"]
    if candle_type not in valid_candle_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid candle_type. Must be one of: {', '.join(valid_candle_types)}",
        )

    try:
        coin = await sync_to_async(Coin.objects.get)(market_code=market_code)
    except Coin.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coin not found",
        )

    @sync_to_async
    def get_candles():
        queryset = CoinCandle.objects.filter(
            coin=coin,
            candle_type=candle_type
        ).select_related("coin")

        if start_date:
            queryset = queryset.filter(trade_date__gte=start_date)

        if end_date:
            queryset = queryset.filter(trade_date__lte=end_date)

        return list(queryset[:limit])

    candles = await get_candles()

    result = []
    for candle in candles:
        candle_dict = CoinCandleResponse.model_validate(candle).model_dump()
        candle_dict["market_code"] = coin.market_code
        candle_dict["korean_name"] = coin.korean_name
        result.append(CoinCandleResponse(**candle_dict))

    return result
