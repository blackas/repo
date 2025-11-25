from datetime import date
from django.core.management.base import BaseCommand

from apps.stocks.services import (
    sync_stock_master_from_krx,
    sync_daily_prices_from_krx,
)


class Command(BaseCommand):
    help = "Sync Korea stock master & daily prices from KRX/pykrx"

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="Target date in YYYY-MM-DD (default: today)",
        )
        parser.add_argument(
            "--skip-master",
            action="store_true",
            help="Skip stock master sync",
        )

    def handle(self, *args, **options):
        if options["date"]:
            target_date = date.fromisoformat(options["date"])
        else:
            target_date = date.today()

        self.stdout.write(self.style.NOTICE(f"Target date: {target_date}"))

        if not options["skip-master"]:
            self.stdout.write("Syncing stock master...")
            cnt = sync_stock_master_from_krx(target_date)
            self.stdout.write(self.style.SUCCESS(f"Stock master synced: {cnt} items"))

        self.stdout.write("Syncing daily prices...")
        cnt = sync_daily_prices_from_krx(target_date)
        self.stdout.write(self.style.SUCCESS(f"Daily prices synced: {cnt} rows"))
