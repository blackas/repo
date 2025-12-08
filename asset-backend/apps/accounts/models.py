from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.common.managers import WatchListQuerySet


class User(AbstractUser):
    phone_number = models.CharField("전화번호", max_length=20, blank=True, null=True)
    kakao_user_id = models.CharField(
        "카카오 사용자 ID",
        max_length=100,
        blank=True,
        null=True,
        help_text="카카오 알림톡 발송 식별자(수신 번호 등)",
    )
    receive_daily_report = models.BooleanField("일일 리포트 수신 여부", default=True)

    def __str__(self):
        return self.username


class RefreshToken(models.Model):
    """
    Refresh Token 저장 모델
    OAuth 2.0 표준을 따르는 refresh token 관리
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="refresh_tokens", verbose_name="사용자"
    )
    token = models.CharField(
        "토큰 JTI", max_length=500, unique=True, db_index=True, help_text="JWT ID (jti)"
    )
    expires_at = models.DateTimeField("만료 시간", db_index=True)
    created_at = models.DateTimeField("생성 시간", auto_now_add=True)
    revoked_at = models.DateTimeField("무효화 시간", null=True, blank=True)

    # 디바이스 정보 (멀티 플랫폼 지원)
    device_type = models.CharField(
        "디바이스 타입",
        max_length=20,
        choices=[
            ("web", "Web"),
            ("ios", "iOS"),
            ("android", "Android"),
        ],
        null=True,
        blank=True,
    )
    device_id = models.CharField("디바이스 ID", max_length=255, null=True, blank=True)

    class Meta:
        db_table = "refresh_tokens"
        verbose_name = "Refresh Token"
        verbose_name_plural = "Refresh Tokens"
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["expires_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.device_type or 'unknown'} - {self.created_at}"

    def is_valid(self):
        """토큰이 유효한지 확인"""
        return self.revoked_at is None and self.expires_at > timezone.now()

    def revoke(self):
        """토큰 무효화"""
        self.revoked_at = timezone.now()
        self.save(update_fields=["revoked_at"])


class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists")
    name = models.CharField("관심목록 이름", max_length=100, default="기본")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = WatchListQuerySet.as_manager()

    def __str__(self):
        return f"{self.user} - {self.name}"


class WatchListItem(models.Model):
    watchlist = models.ForeignKey(WatchList, on_delete=models.CASCADE, related_name="items")
    stock = models.ForeignKey("stocks.Stock", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("watchlist", "stock")
