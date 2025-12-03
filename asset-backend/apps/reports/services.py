import logging
from datetime import date

from django.db.models import QuerySet

from .models import DailyReport
from apps.stocks.models import DailyPrice
from apps.accounts.models import WatchList
from apps.common.exceptions import ReportGenerationError
from apps.common.utils import log_execution_time
from apps.common.cache import cache_result

logger = logging.getLogger(__name__)


@cache_result(timeout=600, key_prefix="watchlist_top_bottom", use_args=True)
def get_watchlist_top_bottom(user, target_date: date, limit: int = 3):
    """
    사용자 관심목록의 상승/하락 TOP 종목 조회
    """
    try:
        watchlist = WatchList.objects.filter(user=user).order_by("id").first()

        if not watchlist:
            logger.warning(f"No watchlist found for user {user.username}")
            return [], []

        qs: QuerySet[DailyPrice] = DailyPrice.objects.filter(
            trade_date=target_date
        ).select_related("stock")

        qs = qs.filter(stock__in=watchlist.items.values("stock_id"))
        qs = qs.exclude(change_rate__isnull=True)

        if not qs.exists():
            logger.warning(
                f"No price data found for user {user.username} on {target_date}"
            )
            return [], []

        top = list(qs.order_by("-change_rate")[:limit])
        bottom = list(qs.order_by("change_rate")[:limit])

        logger.info(
            f"Found {len(top)} top and {len(bottom)} bottom stocks for user {user.username}"
        )
        return top, bottom
    except Exception as e:
        logger.error(f"Error getting watchlist top/bottom for user {user.username}: {e}")
        raise ReportGenerationError(f"Failed to get watchlist data: {e}")


@log_execution_time
def build_daily_report_text(user, target_date: date) -> str:
    """
    일일 리포트 텍스트 생성
    """
    try:
        logger.info(f"Building daily report for user {user.username} on {target_date}")

        top, bottom = get_watchlist_top_bottom(user, target_date)

        lines: list[str] = [
            f"[{target_date.strftime('%Y-%m-%d')}] 한국 주식 일일 리포트",
            "",
            "▶ 오늘의 관심종목 상승 TOP3",
        ]

        if top:
            for idx, p in enumerate(top, start=1):
                lines.append(
                    f"  {idx}. {p.stock.name}({p.stock.code}) "
                    f"종가 {int(p.close_price)}원, 등락률 {p.change_rate}%"
                )
        else:
            lines.append("  - 데이터 없음 (관심종목 또는 시세 미수집)")

        lines.append("")
        lines.append("▶ 오늘의 관심종목 하락 TOP3")

        if bottom:
            for idx, p in enumerate(bottom, start=1):
                lines.append(
                    f"  {idx}. {p.stock.name}({p.stock.code}) "
                    f"종가 {int(p.close_price)}원, 등락률 {p.change_rate}%"
                )
        else:
            lines.append("  - 데이터 없음")

        lines.append("")
        lines.append("※ 본 리포트는 참고용이며 투자 책임은 본인에게 있습니다.")

        report_text = "\n".join(lines)
        logger.info(f"Successfully built report for user {user.username}")
        return report_text
    except Exception as e:
        logger.error(f"Error building report for user {user.username}: {e}")
        raise ReportGenerationError(f"Failed to build daily report: {e}")


@log_execution_time
def create_daily_report_for_user(user, target_date: date) -> DailyReport:
    """
    사용자별 일일 리포트 생성
    """
    try:
        logger.info(f"Creating daily report for user {user.username} on {target_date}")

        text = build_daily_report_text(user, target_date)

        report, created = DailyReport.objects.update_or_create(
            user=user,
            report_date=target_date,
            defaults={
                "title": f"{target_date.strftime('%Y-%m-%d')} 주식 리포트",
                "body_text": text,
            },
        )

        action = "created" if created else "updated"
        logger.info(f"Successfully {action} report {report.id} for user {user.username}")

        return report
    except Exception as e:
        logger.error(f"Error creating report for user {user.username}: {e}", exc_info=True)
        raise ReportGenerationError(f"Failed to create daily report: {e}")
