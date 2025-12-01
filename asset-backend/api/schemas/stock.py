from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date


class StockBase(BaseModel):
    code: str = Field(..., min_length=6, max_length=10)
    name: str = Field(..., min_length=1, max_length=100)
    market: Optional[str] = Field(None, max_length=20)
    sector: Optional[str] = Field(None, max_length=100)
    listed_at: Optional[date] = None


class StockCreate(StockBase):
    is_active: bool = True


class StockUpdate(BaseModel):
    name: Optional[str] = None
    market: Optional[str] = None
    sector: Optional[str] = None
    listed_at: Optional[date] = None
    is_active: Optional[bool] = None


class StockInDB(StockBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class StockResponse(StockInDB):
    pass
