from datetime import date
from celery import shared_task
from django.contrib.auth import get_user_model

from apps.reports.models import DailyReport
from .models import NotificationLog
from .services.kakao_client import KakaoAlimtalkClient

User = get_user_model()


@shared_task
def send_daily_reports_via_kakao(target_date_str: str | None = None, template_code: str = "DAILY_STOCK_REPORT"):
    if target_date_str:
        target_date = date.fromisoformat(target_date_str)
    else:
        target_date = date.today()

    client = KakaoAlimtalkClient()
    users = User.objects.filter(receive_daily_report=True)

    for user in users:
        if not user.phone_number:
            continue

        try:
            report = DailyReport.objects.get(user=user, report_date=target_date)
        except DailyReport.DoesNotExist:
            continue

        result = client.send_message(
            to_phone=user.phone_number,
            template_code=template_code,
            message=report.body_text,
        )

        NotificationLog.objects.create(
            user=user,
            channel=NotificationLog.CHANNEL_KAKAO,
            message=report.body_text,
            success=(200 <= result["status_code"] < 300),
            response_code=str(result["status_code"]),
            response_body=result["body"],
        )
