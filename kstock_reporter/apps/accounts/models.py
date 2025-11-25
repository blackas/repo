from django.contrib.auth.models import AbstractUser
from django.db import models

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


class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists")
    name = models.CharField("관심목록 이름", max_length=100, default="기본")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.name}"


class WatchListItem(models.Model):
    watchlist = models.ForeignKey(WatchList, on_delete=models.CASCADE, related_name="items")
    stock = models.ForeignKey("stocks.Stock", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("watchlist", "stock")
