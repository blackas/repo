from django.contrib import admin
from django.utils.html import format_html

from .models import DailyReport


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ("user", "report_date", "title", "created_at", "preview")
    list_filter = ("report_date", "created_at")
    search_fields = ("user__username", "title", "body_text")
    date_hierarchy = "report_date"
    readonly_fields = ("created_at", "formatted_body")

    fieldsets = (
        ("기본 정보", {
            "fields": ("user", "report_date", "title")
        }),
        ("리포트 내용", {
            "fields": ("body_text", "formatted_body")
        }),
        ("메타 정보", {
            "fields": ("created_at",)
        }),
    )

    def preview(self, obj):
        preview_text = obj.body_text[:50] + "..." if len(obj.body_text) > 50 else obj.body_text
        return preview_text
    preview.short_description = "미리보기"

    def formatted_body(self, obj):
        return format_html("<pre>{}</pre>", obj.body_text)
    formatted_body.short_description = "리포트 내용 (포맷)"

    def has_add_permission(self, request):
        return False
