# Crypto App - 암호화폐 데이터 수집

Upbit API를 활용한 암호화폐 데이터 자동 수집 기능

## 빠른 시작

### 1. 코인 마스터 수집
```python
from apps.crypto.services import fetch_all_coins

# Upbit의 모든 KRW 마켓 코인 수집
count = fetch_all_coins()
print(f"Collected {count} coins")
```

### 2. 캔들 데이터 수집
```python
from datetime import date, timedelta
from apps.crypto.services import fetch_coin_candles
from apps.crypto.models import Coin

# BTC 30일치 캔들 수집
btc = Coin.objects.get(market_code='KRW-BTC')
end_date = date.today()
start_date = end_date - timedelta(days=30)

count = fetch_coin_candles(btc, start_date, end_date)
print(f"Collected {count} candles")
```

### 3. 일괄 수집 (CoinCollectionConfig 기반)
```python
from apps.crypto.services import bulk_collect_candles
from apps.crypto.models import CoinCollectionConfig

config = CoinCollectionConfig.objects.get(name="주요 코인 일별 수집")
result = bulk_collect_candles(config)
print(f"Success: {result['success_count']}, Failed: {result['fail_count']}")
```

## 모델

### Coin
- market_code (Unique): KRW-BTC, KRW-ETH 등
- korean_name: 한글명
- english_name: 영문명
- is_active: 활성화 여부

### CoinCandle
- coin: Coin FK
- trade_date: 거래일 (Unique with coin)
- OHLCV: open_price, high_price, low_price, close_price, volume
- candle_acc_trade_volume: 누적 거래대금

### CoinCollectionConfig
- name: 설정명
- coins: ManyToMany Coin
- candle_type: days/minutes/weeks/months
- collection_interval: hourly/daily/weekly
- period_days: 수집 기간 (1-200일)

## Celery 태스크

자동 스케줄:
- **07:10**: sync_coin_master_task (코인 마스터 동기화)
- **07:15**: collect_crypto_candles_task (캔들 데이터 수집)

수동 실행:
```python
from apps.crypto.tasks import sync_coin_master_task, collect_crypto_candles_task

sync_coin_master_task.delay()
collect_crypto_candles_task.delay()
```

## Django Admin

- **Coin**: 코인 목록 조회/수정
- **CoinCollectionConfig**: 수집 설정 관리, 재수집 액션
- **CoinCandle**: 캔들 데이터 조회 (읽기 전용)

## 테스트

```bash
# 전체 테스트 실행
pytest apps/crypto/tests/ -v

# 특정 테스트
pytest apps/crypto/tests/test_services.py -v

# 커버리지
pytest apps/crypto/tests/ --cov=apps/crypto
```

## 주의사항

1. **Rate Limiting**: Upbit API는 약 6.7 req/sec 제한 (자동 처리됨)
2. **최대 200일**: pyupbit.get_ohlcv()는 최대 200개 캔들만 조회 가능
3. **재시도**: 모든 서비스/태스크는 자동 재시도 지원 (최대 3회)

## 상세 문서

전체 구현 내용은 [docs/crypto_implementation.md](../../docs/crypto_implementation.md) 참조
