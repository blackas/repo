from datetime import date
from celery import shared_task
from django.contrib.auth import get_user_model

from .services import create_daily_report_for_user

User = get_user_model()


@shared_task
def create_daily_reports_for_all_users(target_date_str: str | None = None):
    if target_date_str:
        target_date = date.fromisoformat(target_date_str)
    else:
        target_date = date.today()

    for user in User.objects.filter(receive_daily_report=True):
        create_daily_report_for_user(user, target_date)
