from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class WatchListItemBase(BaseModel):
    stock_id: int


class WatchListItemCreate(WatchListItemBase):
    pass


class WatchListItemInDB(WatchListItemBase):
    id: int
    watchlist_id: int
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class WatchListBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class WatchListCreate(WatchListBase):
    pass


class WatchListUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class WatchListInDB(WatchListBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WatchListResponse(WatchListInDB):
    items: List[WatchListItemInDB] = []
