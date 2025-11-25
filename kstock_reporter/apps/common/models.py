from django.db import models


class TimeStampedModel(models.Model):
    """
    생성/수정 시간을 자동으로 기록하는 추상 모델
    """
    created_at = models.DateTimeField("생성일시", auto_now_add=True)
    updated_at = models.DateTimeField("수정일시", auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    소프트 삭제를 지원하는 추상 모델
    """
    is_deleted = models.BooleanField("삭제 여부", default=False)
    deleted_at = models.DateTimeField("삭제일시", null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()
