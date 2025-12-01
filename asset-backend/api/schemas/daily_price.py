from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date
from decimal import Decimal


class DailyPriceBase(BaseModel):
    stock_id: int
    trade_date: date
    open_price: Decimal = Field(..., ge=0)
    high_price: Decimal = Field(..., ge=0)
    low_price: Decimal = Field(..., ge=0)
    close_price: Decimal = Field(..., ge=0)
    volume: int = Field(..., ge=0)
    amount: Optional[int] = Field(None, ge=0)
    change: Optional[Decimal] = None
    change_rate: Optional[Decimal] = None
    market_cap: Optional[int] = Field(None, ge=0)


class DailyPriceInDB(DailyPriceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DailyPriceResponse(DailyPriceInDB):
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
