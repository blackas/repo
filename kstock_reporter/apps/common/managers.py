"""
최적화된 쿼리셋 매니저
"""
from django.db import models


class OptimizedQuerySetMixin:
    """
    쿼리 최적화를 위한 믹스인
    """

    def with_related(self):
        """
        관련 객체를 한 번에 로드
        서브클래스에서 오버라이드
        """
        return self

    def active(self):
        """
        활성 객체만 조회
        """
        return self.filter(is_active=True)


class StockQuerySet(models.QuerySet, OptimizedQuerySetMixin):
    """
    Stock 모델용 최적화된 쿼리셋
    """

    def active(self):
        return self.filter(is_active=True)

    def by_market(self, market):
        return self.filter(market=market)

    def search(self, query):
        return self.filter(
            models.Q(name__icontains=query) | models.Q(code__icontains=query)
        )


class DailyPriceQuerySet(models.QuerySet, OptimizedQuerySetMixin):
    """
    DailyPrice 모델용 최적화된 쿼리셋
    """

    def with_related(self):
        return self.select_related("stock")

    def for_date(self, date):
        return self.filter(trade_date=date)

    def for_date_range(self, start_date, end_date):
        return self.filter(trade_date__range=[start_date, end_date])

    def top_gainers(self, limit=10):
        return (
            self.exclude(change_rate__isnull=True)
            .order_by("-change_rate")[:limit]
        )

    def top_losers(self, limit=10):
        return (
            self.exclude(change_rate__isnull=True)
            .order_by("change_rate")[:limit]
        )


class WatchListQuerySet(models.QuerySet, OptimizedQuerySetMixin):
    """
    WatchList 모델용 최적화된 쿼리셋
    """

    def with_related(self):
        return self.prefetch_related("items__stock")

    def for_user(self, user):
        return self.filter(user=user)


class DailyReportQuerySet(models.QuerySet, OptimizedQuerySetMixin):
    """
    DailyReport 모델용 최적화된 쿼리셋
    """

    def with_related(self):
        return self.select_related("user")

    def for_user(self, user):
        return self.filter(user=user)

    def for_date(self, date):
        return self.filter(report_date=date)

    def for_date_range(self, start_date, end_date):
        return self.filter(report_date__range=[start_date, end_date])

    def recent(self, limit=30):
        return self.order_by("-report_date")[:limit]


class CoinQuerySet(models.QuerySet):
    """Coin 모델용 커스텀 QuerySet"""

    def active(self):
        """활성화된 코인만 조회"""
        return self.filter(is_active=True)

    def by_market_code(self, market_code: str):
        """마켓 코드로 조회"""
        return self.filter(market_code=market_code)

    def search(self, keyword: str):
        """코인 검색 (마켓 코드, 한글명, 영문명)"""
        return self.filter(
            models.Q(market_code__icontains=keyword) |
            models.Q(korean_name__icontains=keyword) |
            models.Q(english_name__icontains=keyword)
        )


class CoinCandleQuerySet(models.QuerySet):
    """CoinCandle 모델용 커스텀 QuerySet"""

    def for_coin(self, coin):
        """특정 코인의 캔들 데이터"""
        return self.filter(coin=coin)

    def for_date_range(self, start_date, end_date):
        """특정 기간의 캔들 데이터"""
        return self.filter(trade_date__range=[start_date, end_date])

    def latest_candles(self, limit=10):
        """최신 캔들 데이터"""
        return self.order_by('-trade_date')[:limit]
