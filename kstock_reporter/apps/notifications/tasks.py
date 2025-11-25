"""
카카오 알림톡 발송 Celery 태스크
"""
import logging
from datetime import date
from celery import shared_task
from django.contrib.auth import get_user_model

from apps.reports.models import DailyReport
from .models import NotificationLog
from .services.kakao_client import KakaoAlimtalkClient
from apps.common.exceptions import KakaoAPIError

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def send_daily_reports_via_kakao(self, target_date_str: str | None = None, template_code: str = "DAILY_STOCK_REPORT"):
    """
    카카오 알림톡 발송 태스크

    Args:
        target_date_str: 발송할 리포트 날짜 (YYYY-MM-DD 형식), None이면 오늘 날짜
        template_code: 카카오 알림톡 템플릿 코드

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

        logger.info(f"[Task] Starting Kakao notification for {target_date}")

        client = KakaoAlimtalkClient()
        users = User.objects.filter(receive_daily_report=True)
        success_count = 0
        fail_count = 0

        for user in users:
            if not user.phone_number:
                logger.warning(f"[Task] User {user.id} has no phone number, skipping")
                continue

            try:
                report = DailyReport.objects.get(user=user, report_date=target_date)
            except DailyReport.DoesNotExist:
                logger.warning(f"[Task] No report found for user {user.id} on {target_date}")
                continue

            try:
                result = client.send_message(
                    to_phone=user.phone_number,
                    template_code=template_code,
                    message=report.body_text,
                )

                success = (200 <= result["status_code"] < 300)
                NotificationLog.objects.create(
                    user=user,
                    channel=NotificationLog.CHANNEL_KAKAO,
                    message=report.body_text,
                    success=success,
                    response_code=str(result["status_code"]),
                    response_body=result["body"],
                )

                if success:
                    success_count += 1
                    logger.info(f"[Task] Kakao sent to user {user.id}")
                else:
                    fail_count += 1
                    logger.error(f"[Task] Kakao failed for user {user.id}: {result}")

            except KakaoAPIError as e:
                logger.error(f"[Task] Kakao API error for user {user.id}: {e}")
                fail_count += 1
            except Exception as e:
                logger.error(f"[Task] Unexpected error for user {user.id}: {e}", exc_info=True)
                fail_count += 1

        logger.info(f"[Task] Completed Kakao notifications: {success_count} success, {fail_count} failed")
        return {"success": True, "success_count": success_count, "fail_count": fail_count}

    except Exception as exc:
        logger.error(f"[Task] Kakao notification task failed: {exc}", exc_info=True)
        raise self.retry(exc=exc, countdown=300)
