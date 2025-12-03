import pytest
from datetime import date

from apps.reports.models import DailyReport


@pytest.mark.django_db
class TestDailyReportModel:
    def test_create_daily_report(self, user):
        report = DailyReport.objects.create(
            user=user,
            report_date=date.today(),
            title="테스트 리포트",
            body_text="테스트 내용"
        )
        assert report.user == user
        assert report.title == "테스트 리포트"
        assert report.created_at is not None

    def test_daily_report_string_representation(self, daily_report):
        expected = f"{daily_report.user} - {daily_report.report_date}"
        assert str(daily_report) == expected

    def test_daily_report_unique_constraint(self, user):
        today = date.today()
        DailyReport.objects.create(
            user=user,
            report_date=today,
            title="리포트 1",
            body_text="내용 1"
        )
        with pytest.raises(Exception):
            DailyReport.objects.create(
                user=user,
                report_date=today,
                title="리포트 2",
                body_text="내용 2"
            )

    def test_daily_report_ordering(self, user):
        from datetime import timedelta
        today = date.today()
        yesterday = today - timedelta(days=1)

        report_today = DailyReport.objects.create(
            user=user,
            report_date=today,
            title="오늘 리포트",
            body_text="내용"
        )
        report_yesterday = DailyReport.objects.create(
            user=user,
            report_date=yesterday,
            title="어제 리포트",
            body_text="내용"
        )

        reports = list(DailyReport.objects.all())
        assert reports[0] == report_today
        assert reports[1] == report_yesterday
