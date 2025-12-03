from django.contrib import admin
from django.utils.html import format_html

from .models import Stock, DailyPrice


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "market", "sector", "listed_at", "is_active")
    list_filter = ("market", "is_active", "sector")
    search_fields = ("code", "name", "sector")
    list_editable = ("is_active",)
    ordering = ("code",)

    fieldsets = (
        ("기본 정보", {
            "fields": ("code", "name", "market")
        }),
        ("상세 정보", {
            "fields": ("sector", "listed_at", "is_active")
        }),
    )


@admin.register(DailyPrice)
class DailyPriceAdmin(admin.ModelAdmin):
    list_display = (
        "stock_info", "trade_date", "close_price",
        "change_rate_colored", "volume", "market_cap"
    )
    list_filter = ("trade_date", "stock__market")
    search_fields = ("stock__code", "stock__name")
    date_hierarchy = "trade_date"
    autocomplete_fields = ["stock"]

    readonly_fields = ("formatted_prices", "formatted_volume")

    fieldsets = (
        ("기본 정보", {
            "fields": ("stock", "trade_date")
        }),
        ("가격 정보", {
            "fields": ("open_price", "high_price", "low_price", "close_price", "formatted_prices")
        }),
        ("변동 정보", {
            "fields": ("change", "change_rate")
        }),
        ("거래 정보", {
            "fields": ("volume", "amount", "market_cap", "formatted_volume")
        }),
    )

    def stock_info(self, obj):
        return f"{obj.stock.name} ({obj.stock.code})"
    stock_info.short_description = "종목"

    def change_rate_colored(self, obj):
        if obj.change_rate is None:
            return "-"

        color = "red" if obj.change_rate > 0 else "blue" if obj.change_rate < 0 else "gray"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:+.2f}%</span>',
            color, obj.change_rate
        )
    change_rate_colored.short_description = "등락률"

    def formatted_prices(self, obj):
        return format_html(
            "시가: {:,}원<br>고가: {:,}원<br>저가: {:,}원<br>종가: {:,}원",
            int(obj.open_price), int(obj.high_price),
            int(obj.low_price), int(obj.close_price)
        )
    formatted_prices.short_description = "가격 정보"

    def formatted_volume(self, obj):
        if obj.amount:
            return format_html(
                "거래량: {:,}주<br>거래대금: {:,}원",
                obj.volume, obj.amount
            )
        return format_html("거래량: {:,}주", obj.volume)
    formatted_volume.short_description = "거래 정보"
