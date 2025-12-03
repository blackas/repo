"""
Celery 태스크 테스트
"""
import pytest
from unittest.mock import patch
from datetime import date
from celery.exceptions import Retry

from apps.stocks.tasks import sync_stock_master_task, sync_daily_prices_task
from apps.common.exceptions import StockDataFetchError


@pytest.mark.django_db
def test_sync_stock_master_task_success():
    """주식 마스터 동기화 태스크 성공 테스트"""
    with patch('apps.stocks.tasks.sync_stock_master_from_krx') as mock_sync:
        mock_sync.return_value = 100
        result = sync_stock_master_task()

        assert result["success"] is True
        assert result["count"] == 100
        assert "date" in result
        mock_sync.assert_called_once()


@pytest.mark.django_db
def test_sync_stock_master_task_with_date():
    """특정 날짜로 주식 마스터 동기화 태스크 테스트"""
    target_date = "2025-01-15"
    with patch('apps.stocks.tasks.sync_stock_master_from_krx') as mock_sync:
        mock_sync.return_value = 150
        result = sync_stock_master_task(target_date_str=target_date)

        assert result["success"] is True
        assert result["count"] == 150
        assert result["date"] == target_date
        mock_sync.assert_called_once_with(date(2025, 1, 15))


@pytest.mark.django_db
def test_sync_stock_master_task_retry_on_fetch_error():
    """StockDataFetchError 발생 시 재시도 테스트"""
    with patch('apps.stocks.tasks.sync_stock_master_from_krx') as mock_sync:
        mock_sync.side_effect = StockDataFetchError("API error")

        # Celery의 retry를 모킹
        with patch.object(sync_stock_master_task, 'retry', side_effect=Retry("Retry called")) as mock_retry:
            with pytest.raises(Retry):
                sync_stock_master_task()

            mock_retry.assert_called_once()
            # retry 호출 시 exc 인자 확인
            call_args = mock_retry.call_args
            assert isinstance(call_args.kwargs['exc'], StockDataFetchError)


@pytest.mark.django_db
def test_sync_stock_master_task_retry_on_general_exception():
    """일반 예외 발생 시 재시도 테스트"""
    with patch('apps.stocks.tasks.sync_stock_master_from_krx') as mock_sync:
        mock_sync.side_effect = Exception("Unexpected error")

        with patch.object(sync_stock_master_task, 'retry', side_effect=Retry("Retry called")) as mock_retry:
            with pytest.raises(Retry):
                sync_stock_master_task()

            mock_retry.assert_called_once()
            # retry 호출 시 exc 인자 확인
            call_args = mock_retry.call_args
            assert isinstance(call_args.kwargs['exc'], Exception)


@pytest.mark.django_db
def test_sync_daily_prices_task_success():
    """일별 가격 동기화 태스크 성공 테스트"""
    with patch('apps.stocks.tasks.sync_daily_prices_from_krx') as mock_sync:
        mock_sync.return_value = 500
        result = sync_daily_prices_task()

        assert result["success"] is True
        assert result["count"] == 500
        assert "date" in result
        mock_sync.assert_called_once()


@pytest.mark.django_db
def test_sync_daily_prices_task_with_date():
    """특정 날짜로 일별 가격 동기화 태스크 테스트"""
    target_date = "2025-01-15"
    with patch('apps.stocks.tasks.sync_daily_prices_from_krx') as mock_sync:
        mock_sync.return_value = 600
        result = sync_daily_prices_task(target_date_str=target_date)

        assert result["success"] is True
        assert result["count"] == 600
        assert result["date"] == target_date
        mock_sync.assert_called_once_with(date(2025, 1, 15))


@pytest.mark.django_db
def test_sync_daily_prices_task_retry_on_fetch_error():
    """StockDataFetchError 발생 시 재시도 테스트"""
    with patch('apps.stocks.tasks.sync_daily_prices_from_krx') as mock_sync:
        mock_sync.side_effect = StockDataFetchError("API error")

        with patch.object(sync_daily_prices_task, 'retry', side_effect=Retry("Retry called")) as mock_retry:
            with pytest.raises(Retry):
                sync_daily_prices_task()

            mock_retry.assert_called_once()
            call_args = mock_retry.call_args
            assert isinstance(call_args.kwargs['exc'], StockDataFetchError)


@pytest.mark.django_db
def test_sync_daily_prices_task_retry_on_general_exception():
    """일반 예외 발생 시 재시도 테스트"""
    with patch('apps.stocks.tasks.sync_daily_prices_from_krx') as mock_sync:
        mock_sync.side_effect = Exception("Unexpected error")

        with patch.object(sync_daily_prices_task, 'retry', side_effect=Retry("Retry called")) as mock_retry:
            with pytest.raises(Retry):
                sync_daily_prices_task()

            mock_retry.assert_called_once()
            call_args = mock_retry.call_args
            assert isinstance(call_args.kwargs['exc'], Exception)
