from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, WatchList, WatchListItem


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "phone_number", "receive_daily_report", "is_staff")
    list_filter = ("receive_daily_report", "is_staff", "is_active")
    search_fields = ("username", "email", "phone_number", "kakao_user_id")

    fieldsets = BaseUserAdmin.fieldsets + (
        ("추가 정보", {
            "fields": ("phone_number", "kakao_user_id", "receive_daily_report")
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("추가 정보", {
            "fields": ("phone_number", "kakao_user_id", "receive_daily_report")
        }),
    )


class WatchListItemInline(admin.TabularInline):
    model = WatchListItem
    extra = 1
    autocomplete_fields = ["stock"]


@admin.register(WatchList)
class WatchListAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "created_at", "items_count")
    list_filter = ("created_at",)
    search_fields = ("user__username", "name")
    inlines = [WatchListItemInline]

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "종목 수"


@admin.register(WatchListItem)
class WatchListItemAdmin(admin.ModelAdmin):
    list_display = ("watchlist", "stock")
    list_filter = ("watchlist__user",)
    search_fields = ("watchlist__name", "stock__name", "stock__code")
    autocomplete_fields = ["watchlist", "stock"]
