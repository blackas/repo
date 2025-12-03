from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import date

from api.schemas import DailyReportResponse
from api.dependencies import get_current_user
from apps.accounts.models import User
from apps.reports.models import DailyReport

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/", response_model=List[DailyReportResponse])
async def list_reports(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 30,
    current_user: User = Depends(get_current_user),
):
    """
    현재 사용자의 리포트 목록 조회
    """
    queryset = DailyReport.objects.filter(user=current_user).select_related("user")

    if start_date:
        queryset = queryset.filter(report_date__gte=start_date)

    if end_date:
        queryset = queryset.filter(report_date__lte=end_date)

    reports = queryset[skip : skip + limit]

    result = []
    for report in reports:
        report_dict = DailyReportResponse.model_validate(report).model_dump()
        report_dict["username"] = report.user.username
        result.append(DailyReportResponse(**report_dict))

    return result


@router.get("/{report_id}", response_model=DailyReportResponse)
async def read_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    특정 리포트 조회
    """
    try:
        report = DailyReport.objects.select_related("user").get(
            id=report_id, user=current_user
        )
    except DailyReport.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    report_dict = DailyReportResponse.model_validate(report).model_dump()
    report_dict["username"] = report.user.username

    return DailyReportResponse(**report_dict)


@router.get("/date/{report_date}", response_model=DailyReportResponse)
async def read_report_by_date(
    report_date: date,
    current_user: User = Depends(get_current_user),
):
    """
    특정 날짜의 리포트 조회
    """
    try:
        report = DailyReport.objects.select_related("user").get(
            report_date=report_date, user=current_user
        )
    except DailyReport.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found for this date",
        )

    report_dict = DailyReportResponse.model_validate(report).model_dump()
    report_dict["username"] = report.user.username

    return DailyReportResponse(**report_dict)
