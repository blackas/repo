from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.html import format_html
from django import forms

from .models import Coin, CoinCandle, CoinCollectionConfig


class RecollectCandlesForm(forms.Form):
    """재수집 액션용 폼"""
    start_date = forms.DateField(
        label="시작일",
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="재수집할 시작 날짜"
    )
    end_date = forms.DateField(
        label="종료일",
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="재수집할 종료 날짜"
    )


@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    """암호화폐 코인 관리"""
    list_display = ('market_code', 'korean_name', 'english_name', 'is_active_display', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('market_code', 'korean_name', 'english_name')
    ordering = ('market_code',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('기본 정보', {
            'fields': ('market_code', 'korean_name', 'english_name')
        }),
        ('상태', {
            'fields': ('is_active',)
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_active_display(self, obj):
        """활성 상태 표시"""
        if obj.is_active:
            return format_html('<span style="color: green;">●</span> 활성')
        return format_html('<span style="color: red;">●</span> 비활성')
    is_active_display.short_description = '상태'


@admin.register(CoinCollectionConfig)
class CoinCollectionConfigAdmin(admin.ModelAdmin):
    """암호화폐 수집 설정 관리"""
    list_display = ('name', 'candle_type', 'collection_interval', 'period_days', 'is_active_display', 'coin_count', 'created_at')
    list_filter = ('is_active', 'candle_type', 'collection_interval', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('coins',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    actions = ['recollect_candles_action']

    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'is_active')
        }),
        ('수집 설정', {
            'fields': ('candle_type', 'collection_interval', 'period_days')
        }),
        ('수집 대상 코인', {
            'fields': ('coins',)
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_active_display(self, obj):
        """활성 상태 표시"""
        if obj.is_active:
            return format_html('<span style="color: green;">●</span> 활성')
        return format_html('<span style="color: red;">●</span> 비활성')
    is_active_display.short_description = '상태'

    def coin_count(self, obj):
        """선택된 코인 수"""
        return obj.coins.count()
    coin_count.short_description = '코인 수'

    def get_urls(self):
        """커스텀 URL 추가"""
        urls = super().get_urls()
        custom_urls = [
            path(
                'recollect-candles/',
                self.admin_site.admin_view(self.recollect_candles_view),
                name='crypto_recollect_candles',
            ),
        ]
        return custom_urls + urls

    def recollect_candles_action(self, request, queryset):
        """선택된 설정의 캔들 데이터 재수집 액션"""
        selected = queryset.values_list('id', flat=True)
        request.session['selected_config_ids'] = list(selected)
        return redirect('admin:crypto_recollect_candles')
    recollect_candles_action.short_description = "선택된 설정의 캔들 데이터 재수집"

    def recollect_candles_view(self, request):
        """재수집 폼 표시 및 처리"""
        selected_ids = request.session.get('selected_config_ids', [])
        configs = CoinCollectionConfig.objects.filter(id__in=selected_ids)

        if request.method == 'POST':
            form = RecollectCandlesForm(request.POST)
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']

                # Celery 태스크 실행
                from apps.crypto.tasks import recollect_candles_task
                for config in configs:
                    recollect_candles_task.delay(
                        config.id,
                        start_date.isoformat(),
                        end_date.isoformat()
                    )

                self.message_user(
                    request,
                    f"{configs.count()}개 설정에 대한 재수집 태스크가 시작되었습니다. ({start_date} ~ {end_date})"
                )
                return redirect('admin:crypto_coincollectionconfig_changelist')
        else:
            form = RecollectCandlesForm()

        context = {
            'form': form,
            'configs': configs,
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }
        return render(request, 'admin/crypto/recollect_candles.html', context)


@admin.register(CoinCandle)
class CoinCandleAdmin(admin.ModelAdmin):
    """암호화폐 캔들 데이터 조회"""
    list_display = ('coin', 'candle_type_display', 'trade_date', 'close_price_display', 'volume_display', 'created_at')
    list_filter = ('candle_type', 'trade_date', 'created_at')
    search_fields = ('coin__market_code', 'coin__korean_name')
    date_hierarchy = 'trade_date'
    ordering = ('-trade_date', 'coin__market_code')
    readonly_fields = ('coin', 'candle_type', 'trade_date', 'open_price', 'high_price', 'low_price',
                      'close_price', 'volume', 'candle_acc_trade_volume', 'created_at', 'updated_at')

    # 수정 불가 (조회만 가능)
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        ('기본 정보', {
            'fields': ('coin', 'candle_type', 'trade_date')
        }),
        ('가격 정보', {
            'fields': ('open_price', 'high_price', 'low_price', 'close_price')
        }),
        ('거래량 정보', {
            'fields': ('volume', 'candle_acc_trade_volume')
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def candle_type_display(self, obj):
        """캔들 타입 표시"""
        candle_types = {'days': '일봉', 'weeks': '주봉', 'months': '월봉'}
        return candle_types.get(obj.candle_type, obj.candle_type)
    candle_type_display.short_description = '캔들 타입'

    def close_price_display(self, obj):
        """종가 표시 (천단위 구분)"""
        return f"{obj.close_price:,.2f} KRW"
    close_price_display.short_description = '종가'

    def volume_display(self, obj):
        """거래량 표시"""
        return f"{obj.volume:,.8f}"
    volume_display.short_description = '거래량'
