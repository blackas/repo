import pytest

from apps.notifications.models import NotificationLog


@pytest.mark.django_db
class TestNotificationLogModel:
    def test_create_notification_log(self, user):
        log = NotificationLog.objects.create(
            user=user,
            channel="kakao",
            message="테스트 메시지",
            success=True,
            response_code="200"
        )
        assert log.user == user
        assert log.channel == "kakao"
        assert log.success is True

    def test_notification_log_channel_choices(self):
        assert NotificationLog.CHANNEL_KAKAO == "kakao"
        assert len(NotificationLog.CHANNEL_CHOICES) == 1

    def test_notification_log_with_response(self, user):
        log = NotificationLog.objects.create(
            user=user,
            channel="kakao",
            message="메시지",
            success=True,
            response_code="200",
            response_body='{"status": "success"}'
        )
        assert log.response_body is not None
        assert "success" in log.response_body

    def test_notification_log_failure(self, user):
        log = NotificationLog.objects.create(
            user=user,
            channel="kakao",
            message="메시지",
            success=False,
            response_code="500",
            response_body='{"error": "Internal Server Error"}'
        )
        assert log.success is False
        assert log.response_code == "500"
