"""
일일 리포트 생성 Celery 태스크
"""
import logging
from datetime import date
from celery import shared_task
from django.contrib.auth import get_user_model

from .services import create_daily_report_for_user
from apps.common.exceptions import ReportGenerationError

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def create_daily_reports_for_all_users(self, target_date_str: str | None = None):
    """
    모든 사용자의 일일 리포트 생성 태스크

    Args:
        target_date_str: 리포트 생성 날짜 (YYYY-MM-DD 형식), None이면 오늘 날짜

    Returns:
        dict: 성공 여부, 성공 건수, 실패 건수

    Raises:
        Retry: 전체 태스크 실패 시 재시도
    """
    try:
        if target_date_str:
            target_date = date.fromisoformat(target_date_str)
        else:
            target_date = date.today()

        logger.info(f"[Task] Starting daily reports generation for {target_date}")

        users = User.objects.filter(receive_daily_report=True)
        success_count = 0
        fail_count = 0

        for user in users:
            try:
                create_daily_report_for_user(user, target_date)
                success_count += 1
            except ReportGenerationError as e:
                logger.error(f"[Task] Failed to create report for user {user.id}: {e}")
                fail_count += 1
            except Exception as e:
                logger.error(f"[Task] Unexpected error for user {user.id}: {e}", exc_info=True)
                fail_count += 1

        logger.info(f"[Task] Completed daily reports: {success_count} success, {fail_count} failed")
        return {"success": True, "success_count": success_count, "fail_count": fail_count}

    except Exception as exc:
        logger.error(f"[Task] Daily reports task failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=300)
