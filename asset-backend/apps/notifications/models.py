from django.conf import settings
from django.db import models

class NotificationLog(models.Model):
    CHANNEL_KAKAO = "kakao"
    CHANNEL_CHOICES = [
        (CHANNEL_KAKAO, "카카오 알림톡"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    channel = models.CharField("채널", max_length=20, choices=CHANNEL_CHOICES)
    message = models.TextField("메시지 내용")
    sent_at = models.DateTimeField("발송 시간", auto_now_add=True)
    success = models.BooleanField("성공 여부", default=False)
    response_code = models.CharField("응답 코드", max_length=50, blank=True, null=True)
    response_body = models.TextField("응답 본문", blank=True, null=True)
