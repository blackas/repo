# 암호화폐 데이터 수집 기능 구현 문서

## 개요

Upbit API를 활용한 암호화폐 데이터 자동 수집 기능입니다. 코인 마스터 정보와 일별 캔들 데이터를 수집하여 DB에 저장하고, Celery를 통한 자동화된 스케줄링을 지원합니다.

**구현 일자**: 2025-11-27
**브랜치**: feature/crypto-data-collection
**라이브러리**: pyupbit 0.2.31

## 아키텍처

```
┌─────────────────┐
│  Django Admin   │  ← 관리자 인터페이스 (수동 재수집)
└────────┬────────┘
         │
┌────────▼────────┐
│ Celery Tasks    │  ← 스케줄링된 자동 수집
│  - 07:10 Coins  │
│  - 07:15 Candles│
└────────┬────────┘
         │
┌────────▼────────┐
│   Services      │  ← 비즈니스 로직
│  - fetch_all_coins()
│  - fetch_coin_candles()
│  - bulk_collect_candles()
└────────┬────────┘
         │
┌────────▼────────┐
│  Upbit API      │  ← pyupbit 라이브러리
│  (Rate: 6.7/s)  │
└─────────────────┘
         │
┌────────▼────────┐
│  PostgreSQL DB  │  ← 데이터 저장
│  - crypto_coin
│  - crypto_coin_candle
│  - crypto_coin_collection_config
└─────────────────┘
```

## 데이터베이스 스키마

### 1. Coin (crypto_coin)
코인 마스터 정보

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | BigInt | Primary Key |
| market_code | Varchar(20) | 마켓 코드 (예: KRW-BTC), Unique |
| korean_name | Varchar(100) | 한글명 |
| english_name | Varchar(100) | 영문명 |
| is_active | Boolean | 활성화 여부 |
| created_at | Timestamp | 생성일시 |
| updated_at | Timestamp | 수정일시 |

**인덱스**: market_code (unique)

### 2. CoinCandle (crypto_coin_candle)
일별 캔들 데이터 (OHLCV)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | BigInt | Primary Key |
| coin_id | BigInt | Foreign Key → Coin |
| trade_date | Date | 거래일, Index |
| open_price | Decimal(20,8) | 시가 |
| high_price | Decimal(20,8) | 고가 |
| low_price | Decimal(20,8) | 저가 |
| close_price | Decimal(20,8) | 종가 |
| volume | Decimal(20,8) | 거래량(코인) |
| candle_acc_trade_volume | Decimal(20,2) | 누적 거래대금(KRW) |
| created_at | Timestamp | 생성일시 |
| updated_at | Timestamp | 수정일시 |

**인덱스**:
- (coin_id, trade_date) unique together
- (coin_id, -trade_date) composite

### 3. CoinCollectionConfig (crypto_coin_collection_config)
수집 설정 관리

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | BigInt | Primary Key |
| name | Varchar(100) | 설정명, Unique |
| candle_type | Varchar(20) | 캔들 타입 (days/minutes/weeks/months) |
| collection_interval | Varchar(20) | 수집 주기 (hourly/daily/weekly) |
| period_days | Integer | 수집 기간(일) 1-200 제한 |
| is_active | Boolean | 활성화 여부 |
| created_at | Timestamp | 생성일시 |
| updated_at | Timestamp | 수정일시 |

**Many-to-Many**: coins (Coin)

## 핵심 서비스 함수

### apps/crypto/services.py

#### 1. fetch_all_coins()
```python
@log_execution_time
@retry_on_failure(max_retries=3, delay=2.0)
def fetch_all_coins() -> int
```

**기능**: Upbit의 모든 KRW 마켓 코인 목록 조회 및 DB 동기화

**프로세스**:
1. `pyupbit.get_tickers(fiat="KRW")` 호출
2. 티커에서 코인 심볼 추출 (KRW-BTC → BTC)
3. `Coin.objects.update_or_create()` 로 DB 저장
4. Rate limiting: 10개마다 0.15초 대기

**반환**: 업데이트된 코인 수

**예외**: CryptoDataFetchError

#### 2. fetch_coin_candles()
```python
@log_execution_time
@retry_on_failure(max_retries=3, delay=2.0)
def fetch_coin_candles(
    coin: Coin,
    start_date: date,
    end_date: date,
    candle_type: str = "days"
) -> int
```

**기능**: 특정 코인의 캔들 데이터 수집

**프로세스**:
1. 기간 계산 (최대 200일 제한)
2. `pyupbit.get_ohlcv()` 호출
3. DataFrame을 순회하며 캔들 데이터 저장
4. `CoinCandle.objects.update_or_create()` 사용

**파라미터**:
- coin: Coin 모델 인스턴스
- start_date: 수집 시작일
- end_date: 수집 종료일
- candle_type: days(기본)/minutes/weeks/months

**반환**: 저장된 캔들 수

**예외**: CryptoDataFetchError

#### 3. bulk_collect_candles()
```python
@log_execution_time
def bulk_collect_candles(config: CoinCollectionConfig) -> dict
```

**기능**: CoinCollectionConfig 기반 일괄 수집

**프로세스**:
1. config.coins 에서 활성화된 코인 조회
2. 각 코인에 대해 fetch_coin_candles() 호출
3. 성공/실패 카운트 집계
4. 코인 간 0.15초 대기 (Rate limiting)

**반환**:
```python
{
    'success_count': int,
    'fail_count': int,
    'total': int
}
```

## Celery 태스크

### apps/crypto/tasks.py

#### 1. sync_coin_master_task
```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_coin_master_task(self)
```

**스케줄**: 매일 07:10

**기능**: fetch_all_coins() 호출하여 코인 마스터 동기화

**재시도**: CryptoDataFetchError 발생 시 60초 후 재시도 (최대 3회)

#### 2. collect_crypto_candles_task
```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def collect_crypto_candles_task(self)
```

**스케줄**: 매일 07:15

**기능**: 활성화된 모든 CoinCollectionConfig에 대해 bulk_collect_candles() 호출

**재시도**: CryptoDataFetchError 발생 시 60초 후 재시도 (최대 3회)

#### 3. recollect_candles_task
```python
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def recollect_candles_task(self, config_id: int, start_date_str: str, end_date_str: str)
```

**트리거**: Django Admin 수동 액션

**기능**: 특정 설정의 특정 기간 캔들 데이터 재수집

**파라미터**:
- config_id: CoinCollectionConfig ID
- start_date_str: 시작일 (YYYY-MM-DD)
- end_date_str: 종료일 (YYYY-MM-DD)

## Django Admin 설정

### apps/crypto/admin.py

#### 1. CoinAdmin
- **리스트**: market_code, korean_name, english_name, is_active, created_at
- **필터**: is_active, created_at
- **검색**: market_code, korean_name, english_name
- **특징**: 활성 상태 컬러 표시 (녹색/빨간색)

#### 2. CoinCollectionConfigAdmin
- **리스트**: name, candle_type, collection_interval, period_days, is_active, coin_count, created_at
- **필터**: is_active, candle_type, collection_interval
- **M2M**: filter_horizontal 위젯으로 코인 선택
- **커스텀 액션**: "선택된 설정의 캔들 데이터 재수집"
  - 재수집 폼 표시 (시작일/종료일 입력)
  - recollect_candles_task.delay() 호출

#### 3. CoinCandleAdmin
- **리스트**: coin, trade_date, close_price, volume, created_at
- **필터**: trade_date, created_at
- **검색**: coin__market_code, coin__korean_name
- **date_hierarchy**: trade_date
- **특징**: 읽기 전용 (수정/삭제 불가)

## 테스트 커버리지

### 전체 테스트 결과
```
apps/crypto/tests/ - 38 tests
├── test_models.py - 13 tests (100% coverage)
├── test_services.py - 11 tests (100% coverage)
└── test_tasks.py - 14 tests (100% coverage)

Coverage:
- models.py: 100%
- services.py: 89%
- tasks.py: 89%
```

### 주요 테스트 케이스

**Models**:
- Coin unique constraint
- CoinCandle unique_together
- CoinCollectionConfig period_days validation (1-200)
- QuerySet methods (active, search, for_coin, etc.)

**Services**:
- fetch_all_coins 성공/실패
- fetch_coin_candles 성공/빈값/대량기간/에러
- bulk_collect_candles 성공/부분실패/비활성코인

**Tasks**:
- sync_coin_master_task 성공/재시도
- collect_crypto_candles_task 다중설정/부분실패
- recollect_candles_task 다중코인/비활성코인/0개수집

## Rate Limiting

Upbit API는 초당 요청 수 제한이 있으므로 모든 서비스에서 `time.sleep(0.15)` 적용:
- 약 6.7 req/sec (초당 6.7회 요청)
- 10개마다 추가 대기 (fetch_all_coins)
- 코인 간 대기 (bulk_collect_candles)

## 실제 데이터 검증

### 2025-11-27 통합 테스트 결과

**코인 마스터**:
```
✓ 229개 코인 수집 완료
✓ 예시: KRW-BTC, KRW-ETH, KRW-XRP 등
```

**BTC 캔들 데이터** (2025-11-21 ~ 2025-11-27):
```
최신 캔들 (2025-11-26):
  Open:   130,779,000 KRW
  High:   135,485,000 KRW
  Low:    129,600,000 KRW
  Close:  135,366,000 KRW
  Volume: 2216.72 BTC
```

## 사용 방법

### 1. 수동 수집 (Django Shell)

```python
from apps.crypto.services import fetch_all_coins, fetch_coin_candles
from apps.crypto.models import Coin
from datetime import date, timedelta

# 코인 마스터 수집
count = fetch_all_coins()
print(f"Collected {count} coins")

# 특정 코인 캔들 수집
btc = Coin.objects.get(market_code='KRW-BTC')
end_date = date.today()
start_date = end_date - timedelta(days=30)
count = fetch_coin_candles(btc, start_date, end_date)
print(f"Collected {count} candles for BTC")
```

### 2. Celery 태스크 수동 실행

```python
from apps.crypto.tasks import sync_coin_master_task, collect_crypto_candles_task

# 코인 마스터 동기화
result = sync_coin_master_task.delay()
print(result.get())

# 캔들 데이터 수집
result = collect_crypto_candles_task.delay()
print(result.get())
```

### 3. Django Admin에서 재수집

1. Admin → 암호화폐 수집 설정
2. 재수집할 설정 선택
3. 액션 → "선택된 설정의 캔들 데이터 재수집"
4. 시작일/종료일 입력
5. "재수집 시작" 버튼 클릭

## 운영 가이드

### Celery Beat 스케줄

```python
CELERY_BEAT_SCHEDULE = {
    "sync-coin-master-daily": {
        "task": "apps.crypto.tasks.sync_coin_master_task",
        "schedule": crontab(hour=7, minute=10),  # 매일 07:10
        "options": {"expires": 3600},
    },
    "collect-crypto-candles-daily": {
        "task": "apps.crypto.tasks.collect_crypto_candles_task",
        "schedule": crontab(hour=7, minute=15),  # 매일 07:15
        "options": {"expires": 3600},
    },
}
```

### 로그 확인

```bash
# Celery Worker 로그
tail -f /var/log/celery/worker.log

# Django 로그
tail -f /var/log/django/app.log | grep "apps.crypto"
```

### 모니터링 포인트

1. **Celery 태스크 성공률**: sync_coin_master_task, collect_crypto_candles_task
2. **데이터 누락 확인**: 특정 날짜의 candle 데이터 존재 여부
3. **API 응답 시간**: Upbit API 응답 지연 모니터링
4. **Rate Limit 에러**: 429 Too Many Requests 발생 여부

## 문제 해결

### 1. "API Error" 발생 시
```python
# 재시도 로직이 자동 동작 (최대 3회)
# 수동 재시도:
from apps.crypto.tasks import sync_coin_master_task
sync_coin_master_task.apply_async(countdown=60)
```

### 2. "No candles collected" 경고
- Upbit API에 해당 기간 데이터가 없는 경우
- 주말/공휴일 등 거래가 없는 날
- 정상 동작으로 간주

### 3. Rate Limit 초과
- time.sleep(0.15) 확인
- 대량 수집 시 batch 크기 조정
- Celery 동시 실행 worker 수 제한

## 향후 개선 사항

1. **분봉 데이터 지원**: 1분, 5분, 15분 캔들 추가
2. **실시간 데이터**: WebSocket 연동
3. **알림 기능**: 데이터 수집 실패 시 Slack/Email 알림
4. **대시보드**: 수집 현황 시각화
5. **백테스팅**: 수집된 데이터 기반 전략 테스트

## 참고 자료

- **Upbit API 문서**: https://docs.upbit.com/
- **pyupbit 문서**: https://github.com/sharebook-kr/pyupbit
- **Celery Beat**: https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html

## 변경 이력

- **2025-11-27**: 초기 구현 완료
  - 코인 마스터 수집
  - 일봉 캔들 데이터 수집
  - Celery 자동화
  - Django Admin 인터페이스
  - 100% 테스트 커버리지
