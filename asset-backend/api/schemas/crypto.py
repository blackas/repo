"""
암호화폐 API 스키마
"""
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from decimal import Decimal


class CoinResponse(BaseModel):
    """코인 정보 응답"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    market_code: str
    korean_name: str
    english_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CoinCandleResponse(BaseModel):
    """코인 캔들 데이터 응답"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    candle_type: str
    trade_date: date
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    candle_acc_trade_volume: Decimal | None = None

    # 추가 정보
    market_code: str | None = None
    korean_name: str | None = None
