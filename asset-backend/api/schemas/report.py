from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime


class DailyReportBase(BaseModel):
    report_date: date
    title: str = Field(..., max_length=200)
    body_text: str


class DailyReportInDB(DailyReportBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailyReportResponse(DailyReportInDB):
    username: str
