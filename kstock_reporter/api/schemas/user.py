from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    receive_daily_report: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    receive_daily_report: Optional[bool] = None
    kakao_user_id: Optional[str] = None


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_staff: bool
    is_superuser: bool
    date_joined: datetime
    kakao_user_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInDB):
    pass
