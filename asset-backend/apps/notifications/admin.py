from django.contrib import admin
from django.utils.html import format_html

from .models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = (
        "user", "channel", "sent_at", "success_status",
        "response_code", "message_preview"
    )
    list_filter = ("channel", "success", "sent_at")
    search_fields = ("user__username", "message", "response_code")
    date_hierarchy = "sent_at"
    readonly_fields = ("sent_at", "formatted_message", "formatted_response")

    fieldsets = (
        ("기본 정보", {
            "fields": ("user", "channel", "sent_at")
        }),
        ("메시지", {
            "fields": ("message", "formatted_message")
        }),
        ("발송 결과", {
            "fields": ("success", "response_code", "response_body", "formatted_response")
        }),
    )

    def success_status(self, obj):
        if obj.success:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ 성공</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ 실패</span>'
        )
    success_status.short_description = "발송 상태"

    def message_preview(self, obj):
        preview = obj.message[:30] + "..." if len(obj.message) > 30 else obj.message
        return preview
    message_preview.short_description = "메시지 미리보기"

    def formatted_message(self, obj):
        return format_html("<pre>{}</pre>", obj.message)
    formatted_message.short_description = "메시지 내용"

    def formatted_response(self, obj):
        if obj.response_body:
            return format_html("<pre>{}</pre>", obj.response_body)
        return "-"
    formatted_response.short_description = "응답 내용"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
