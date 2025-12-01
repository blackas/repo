from django.conf import settings
from django.db import models

from apps.common.managers import DailyReportQuerySet


class DailyReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    report_date = models.DateField("리포트 기준일")
    title = models.CharField("제목", max_length=200)
    body_text = models.TextField("내용")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DailyReportQuerySet.as_manager()

    class Meta:
        unique_together = ("user", "report_date")
        ordering = ["-report_date"]

    def __str__(self):
        return f"{self.user} - {self.report_date}"
