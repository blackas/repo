import pytest
from datetime import date
from unittest.mock import patch, MagicMock
import pandas as pd
from decimal import Decimal

from apps.stocks.services import (
    format_krx_date,
    sync_stock_master_from_krx,
    sync_daily_prices_from_krx
)
from apps.stocks.models import Stock, DailyPrice


@pytest.mark.unit
class TestFormatKrxDate:
    def test_format_krx_date(self):
        test_date = date(2024, 11, 25)
        result = format_krx_date(test_date)
        assert result == "20241125"


@pytest.mark.django_db
class TestSyncStockMasterFromKrx:
    @patch("pykrx.stock.get_market_ticker_list")
    @patch("pykrx.stock.get_market_ticker_name")
    def test_sync_stock_master(self, mock_get_name, mock_get_list):
        """get_stock_market_from_ticker는 try/except로 처리되므로 mock 불필요"""
        mock_get_list.return_value = ["005930", "000660"]
        mock_get_name.side_effect = ["삼성전자", "SK하이닉스"]

        count = sync_stock_master_from_krx(date(2024, 11, 25))

        assert count == 2
        assert Stock.objects.count() == 2
        assert Stock.objects.filter(code="005930").exists()
        assert Stock.objects.filter(code="000660").exists()


@pytest.mark.django_db
class TestSyncDailyPricesFromKrx:
    @patch("pykrx.stock.get_market_ohlcv_by_ticker")
    def test_sync_daily_prices(self, mock_get_ohlcv, stock):
        mock_df = pd.DataFrame({
            "시가": [70000],
            "고가": [71000],
            "저가": [69000],
            "종가": [70500],
            "거래량": [1000000],
            "거래대금": [70500000000],
            "등락": [500],
            "등락률": [0.71]
        }, index=["005930"])

        mock_get_ohlcv.return_value = mock_df

        today = date.today()
        count = sync_daily_prices_from_krx(today)

        assert count == 1
        assert DailyPrice.objects.count() == 1

        price = DailyPrice.objects.first()
        assert price.stock == stock
        assert price.close_price == 70500
        assert price.volume == 1000000
