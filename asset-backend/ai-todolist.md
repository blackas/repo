# 사용자의 최초 요청 (기록용)
asset-backend에 주식 및 암호화폐 캔들이 일별 캔들만 있는것으로 파악되는데 주/월/년 캔들이 있는게 좋은지 판단해서 작업진행해줘. 좋다고 판단되면 아래 순서로 작업 진행해줘.
1. 작업 브랜치 생성
2. 작업 진행
3. 작업 단위로 커밋 생성
4. 작업 내용 PROJECT_ORVERVIEW.md 에 최신화
5. PR 생성

## 사용자가 이후에 추가 요청한 내용들 (기록용)
(없음)

# 작업 목표
- **주식(Stock) 데이터에 주봉/월봉/연봉 캔들 추가**
- **암호화폐(Crypto) 데이터에 주봉/월봉 캔들 활성화**
- **기존 일봉 데이터와 함께 다중 시간대 캔들 지원**
- **API 엔드포인트에서 시간대별 캔들 조회 가능**
- **Celery Task로 자동 집계 및 동기화**
- **프로젝트 문서 업데이트**

# 작업 계획 상세 수준
detail_level = detailed

# 작업 배경

## 현재 상황 분석
### 주식 (apps/stocks)
- **모델**: `DailyPrice` - 일봉 캔들만 저장
- **서비스**: `sync_daily_prices_from_krx()` - pykrx로 일봉만 수집
- **Task**: `sync_daily_prices_task()` - 일별 동기화
- **API**: `/stocks/{stock_code}/prices` - 일봉 데이터만 반환
- **한계**: pykrx는 일봉만 제공하므로, 주/월/년봉은 일봉 데이터를 집계하여 생성해야 함

### 암호화폐 (apps/crypto)
- **모델**: `CoinCandle` - 일봉 캔들만 실제 사용 중
- **서비스**: `fetch_coin_candles()` - candle_type 파라미터 지원 (days, minutes, weeks, months)
- **설정**: `CoinCollectionConfig.CANDLE_TYPE_CHOICES`에 'weeks', 'months' 이미 정의됨
- **Task**: `collect_crypto_candles_task()` - 설정 기반 수집
- **API**: 암호화폐 API 엔드포인트 없음 (미구현)
- **장점**: pyupbit는 주봉/월봉을 직접 제공하므로 별도 집계 불필요

## 판단 결과: 주/월/년 캔들 추가가 필요함

### 추가가 필요한 이유
1. **차트 분석 향상**: 장기 투자자는 주봉/월봉으로 추세를 파악
2. **API 성능 개선**: 1년치 데이터 조회 시 일봉 365개 vs 월봉 12개 → 30배 효율
3. **프론트엔드 부하 감소**: 차트 라이브러리가 적절한 시간 단위 데이터를 받으면 렌더링 성능 향상
4. **기술적 분석 도구**: 이동평균(MA), RSI, MACD 등의 지표는 주/월 단위로도 계산됨
5. **데이터 집계 비용 절감**: 매번 일봉 집계 대신 미리 계산된 주/월봉 제공
6. **암호화폐 인프라 준비됨**: 이미 CoinCollectionConfig에 weeks/months 정의됨

### 구현 전략
- **주식**: 일봉 데이터를 집계하여 주봉/월봉/연봉 생성 (pykrx 제약)
- **암호화폐**: pyupbit API로 주봉/월봉 직접 수집

# 작업 시작 여부
is_execution_started = FALSE

# 모든 목표 달성 여부
is_all_goals_accomplished = FALSE

# 병렬 실행 여부
parallel_requested = FALSE

# 현재 진행 중인 작업
- 사용자의 "작업을 시작하라" 명령 대기 중

# 필요한 사전 지식

## 기술 스택
- **Python**: 3.13.8
- **Django**: 5.1.1
- **FastAPI**: 0.122.0
- **Celery**: 5.5.3 (with Beat for scheduling)
- **Redis**: DB0-DB3 (Broker, Results, Cache, Rate Limiting)
- **PostgreSQL**: 메인 데이터베이스
- **pykrx**: 1.0.51 (한국 주식 데이터)
- **pyupbit**: 0.2.31 (업비트 암호화폐 데이터)

## 프로젝트 구조
```
asset-backend/
├── apps/
│   ├── stocks/          # 주식 데이터 관리
│   │   ├── models.py    # Stock, DailyPrice
│   │   ├── services.py  # KRX 데이터 수집
│   │   └── tasks.py     # Celery 태스크
│   ├── crypto/          # 암호화폐 데이터 관리
│   │   ├── models.py    # Coin, CoinCandle, CoinCollectionConfig
│   │   ├── services.py  # Upbit 데이터 수집
│   │   └── tasks.py     # Celery 태스크
│   └── common/          # 공통 유틸리티
└── api/
    └── v1/
        ├── stocks.py    # 주식 API 엔드포인트
        └── auth.py      # 인증 API
```

## 캔들 시간 단위별 집계 로직
### 주봉 (Weekly Candle)
- **기준**: ISO 주차 (월요일 시작, 일요일 종료)
- **집계**:
  - 시가(open): 주의 첫 거래일 시가
  - 고가(high): 주간 최고가
  - 저가(low): 주간 최저가
  - 종가(close): 주의 마지막 거래일 종가
  - 거래량(volume): 주간 거래량 합계
  - trade_date: 주의 마지막 거래일

### 월봉 (Monthly Candle)
- **기준**: 달력상 월 (1일 ~ 말일)
- **집계**:
  - 시가(open): 월의 첫 거래일 시가
  - 고가(high): 월간 최고가
  - 저가(low): 월간 최저가
  - 종가(close): 월의 마지막 거래일 종가
  - 거래량(volume): 월간 거래량 합계
  - trade_date: 월의 마지막 거래일

### 연봉 (Yearly Candle)
- **기준**: 달력상 연도 (1/1 ~ 12/31)
- **집계**:
  - 시가(open): 연의 첫 거래일 시가
  - 고가(high): 연간 최고가
  - 저가(low): 연간 최저가
  - 종가(close): 연의 마지막 거래일 종가
  - 거래량(volume): 연간 거래량 합계
  - trade_date: 연의 마지막 거래일

# 작업 계획

## Phase 1: 데이터베이스 스키마 설계 및 마이그레이션

### ☐ TODO #1: 주식 주봉/월봉/연봉 모델 추가
**목표**: `apps/stocks/models.py`에 WeeklyPrice, MonthlyPrice, YearlyPrice 모델 추가

**상세 작업**:
1. `WeeklyPrice` 모델 생성
   - 필드: stock(FK), trade_date, open_price, high_price, low_price, close_price, volume, amount, change, change_rate, market_cap
   - Meta: unique_together = ("stock", "trade_date"), ordering = ["-trade_date"]
   - 인덱스: stock + trade_date

2. `MonthlyPrice` 모델 생성
   - WeeklyPrice와 동일한 구조

3. `YearlyPrice` 모델 생성
   - WeeklyPrice와 동일한 구조

4. QuerySet Manager 추가 (apps/common/managers.py)
   - WeeklyPriceQuerySet
   - MonthlyPriceQuerySet
   - YearlyPriceQuerySet

**검증 기준**:
- [ ] 모델 클래스가 올바르게 정의됨
- [ ] unique_together 제약조건이 설정됨
- [ ] 적절한 인덱스가 설정됨

**예상 소요 시간**: 30분

**파일 경로**:
- `apps/stocks/models.py`
- `apps/common/managers.py`

---

### ☐ TODO #2: 암호화폐 주봉/월봉 모델 확장
**목표**: `CoinCandle` 모델에 candle_type 필드 추가로 다중 시간대 지원

**상세 작업**:
1. `CoinCandle` 모델 수정
   - `candle_type` 필드 추가: CharField, choices=['days', 'weeks', 'months'], default='days'
   - unique_together 변경: ("coin", "candle_type", "trade_date")
   - 인덱스 추가: coin + candle_type + trade_date

2. 기존 데이터 마이그레이션
   - 기존 CoinCandle 레코드의 candle_type을 'days'로 설정하는 데이터 마이그레이션 작성

**검증 기준**:
- [ ] candle_type 필드가 추가됨
- [ ] unique_together가 업데이트됨
- [ ] 기존 데이터가 'days'로 마이그레이션됨

**예상 소요 시간**: 30분

**파일 경로**:
- `apps/crypto/models.py`
- `apps/crypto/migrations/XXXX_add_candle_type.py`

---

### ☐ TODO #3: Django 마이그레이션 생성 및 적용
**목표**: 새 모델과 수정사항을 데이터베이스에 반영

**상세 작업**:
```bash
python manage.py makemigrations stocks
python manage.py makemigrations crypto
python manage.py migrate
```

**검증 기준**:
- [ ] 마이그레이션 파일이 생성됨
- [ ] 마이그레이션이 에러 없이 적용됨
- [ ] 데이터베이스 테이블이 생성됨

**예상 소요 시간**: 10분

**커밋 메시지**:
```
feat: Add weekly/monthly/yearly candle models for stocks and crypto

- Add WeeklyPrice, MonthlyPrice, YearlyPrice models for stocks
- Extend CoinCandle with candle_type field for multi-timeframe support
- Add appropriate indexes and unique constraints
- Migrate existing crypto candle data to 'days' type

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Phase 2: 주식 캔들 집계 서비스 구현

### ☐ TODO #4: 주식 주봉 집계 서비스 함수 작성
**목표**: `apps/stocks/services.py`에 `aggregate_weekly_prices()` 함수 추가

**상세 작업**:
1. 함수 시그니처 정의
   ```python
   @log_execution_time
   @transaction.atomic
   def aggregate_weekly_prices(stock: Stock, start_date: date, end_date: date) -> int:
   ```

2. 일봉 데이터를 주 단위로 그룹화 (ISO 주차 기준)
   - Django ORM의 `TruncWeek` 사용
   - 또는 Python의 `date.isocalendar()` 활용

3. 각 주별로 OHLC 집계
   - 시가: Min(trade_date)의 open_price
   - 고가: Max(high_price)
   - 저가: Min(low_price)
   - 종가: Max(trade_date)의 close_price
   - 거래량: Sum(volume)

4. `WeeklyPrice` 모델에 저장

**검증 기준**:
- [ ] 함수가 정상적으로 동작함
- [ ] 집계 로직이 정확함 (테스트 케이스로 검증)
- [ ] 트랜잭션 처리가 올바름

**예상 소요 시간**: 1시간

**파일 경로**:
- `apps/stocks/services.py`

---

### ☐ TODO #5: 주식 월봉 집계 서비스 함수 작성
**목표**: `apps/stocks/services.py`에 `aggregate_monthly_prices()` 함수 추가

**상세 작업**:
1. 함수 시그니처 정의
   ```python
   @log_execution_time
   @transaction.atomic
   def aggregate_monthly_prices(stock: Stock, start_date: date, end_date: date) -> int:
   ```

2. 일봉 데이터를 월 단위로 그룹화
   - Django ORM의 `TruncMonth` 사용
   - 또는 `date.year`, `date.month` 그룹화

3. 각 월별로 OHLC 집계 (주봉과 동일한 로직)

4. `MonthlyPrice` 모델에 저장

**검증 기준**:
- [ ] 함수가 정상적으로 동작함
- [ ] 집계 로직이 정확함
- [ ] 트랜잭션 처리가 올바름

**예상 소요 시간**: 45분

**파일 경로**:
- `apps/stocks/services.py`

---

### ☐ TODO #6: 주식 연봉 집계 서비스 함수 작성
**목표**: `apps/stocks/services.py`에 `aggregate_yearly_prices()` 함수 추가

**상세 작업**:
1. 함수 시그니처 정의
   ```python
   @log_execution_time
   @transaction.atomic
   def aggregate_yearly_prices(stock: Stock, start_date: date, end_date: date) -> int:
   ```

2. 일봉 데이터를 연 단위로 그룹화
   - Django ORM의 `TruncYear` 사용

3. 각 연도별로 OHLC 집계

4. `YearlyPrice` 모델에 저장

**검증 기준**:
- [ ] 함수가 정상적으로 동작함
- [ ] 집계 로직이 정확함
- [ ] 트랜잭션 처리가 올바름

**예상 소요 시간**: 45분

**파일 경로**:
- `apps/stocks/services.py`

**커밋 메시지**:
```
feat: Implement stock candle aggregation services

- Add aggregate_weekly_prices() for weekly OHLC aggregation
- Add aggregate_monthly_prices() for monthly OHLC aggregation
- Add aggregate_yearly_prices() for yearly OHLC aggregation
- Use Django ORM Trunc functions for date grouping

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Phase 3: 암호화폐 주봉/월봉 수집 서비스 구현

### ☐ TODO #7: 암호화폐 주봉/월봉 직접 수집 활성화
**목표**: `apps/crypto/services.py`의 `fetch_coin_candles()` 함수 검증 및 주봉/월봉 수집 테스트

**상세 작업**:
1. 기존 `fetch_coin_candles()` 함수 검토
   - candle_type 파라미터가 'weeks', 'months'를 지원하는지 확인
   - pyupbit.get_ohlcv()가 interval='weeks', 'months'를 지원하는지 검증

2. 필요 시 함수 수정
   - candle_type과 CoinCandle.candle_type 필드 연결
   - 저장 시 candle_type 명시

3. 수동 테스트
   ```python
   from apps.crypto.services import fetch_coin_candles
   from apps.crypto.models import Coin
   coin = Coin.objects.get(market_code='KRW-BTC')
   fetch_coin_candles(coin, start_date, end_date, candle_type='weeks')
   ```

**검증 기준**:
- [ ] 주봉 데이터가 정상적으로 수집됨
- [ ] 월봉 데이터가 정상적으로 수집됨
- [ ] candle_type이 올바르게 저장됨

**예상 소요 시간**: 30분

**파일 경로**:
- `apps/crypto/services.py`

---

### ☐ TODO #8: 암호화폐 수집 설정(CoinCollectionConfig) 활성화
**목표**: Admin에서 주봉/월봉 수집 설정을 생성할 수 있도록 활성화

**상세 작업**:
1. `apps/crypto/admin.py`에서 CoinCollectionConfig 확인
   - candle_type 필드가 Admin UI에 노출되는지 확인
   - 'weeks', 'months' 선택 가능한지 확인

2. Admin에서 테스트 설정 생성
   - 주봉 수집 설정: candle_type='weeks', collection_interval='weekly'
   - 월봉 수집 설정: candle_type='months', collection_interval='monthly'

**검증 기준**:
- [ ] Admin UI에서 주봉/월봉 설정 생성 가능
- [ ] 설정이 올바르게 저장됨

**예상 소요 시간**: 15분

**파일 경로**:
- `apps/crypto/admin.py`

**커밋 메시지**:
```
feat: Enable weekly/monthly crypto candle collection

- Activate weekly/monthly candle collection in fetch_coin_candles()
- Verify pyupbit API support for 'weeks' and 'months' intervals
- Enable CoinCollectionConfig for multi-timeframe settings

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Phase 4: Celery Task 추가

### ☐ TODO #9: 주식 주봉/월봉/연봉 집계 Task 추가
**목표**: `apps/stocks/tasks.py`에 집계 Celery Task 추가

**상세 작업**:
1. `aggregate_weekly_prices_task()` 추가
   ```python
   @shared_task(bind=True, max_retries=3, default_retry_delay=60)
   def aggregate_weekly_prices_task(self, stock_code: str = None, start_date_str: str = None, end_date_str: str = None):
   ```
   - stock_code가 None이면 모든 주식 처리
   - 날짜 파라미터 기본값: 최근 1년

2. `aggregate_monthly_prices_task()` 추가
   - 동일한 구조

3. `aggregate_yearly_prices_task()` 추가
   - 동일한 구조

4. 통합 Task 추가 (선택사항)
   ```python
   @shared_task
   def aggregate_all_stock_candles_task():
       # 주봉, 월봉, 연봉 순차 실행
   ```

**검증 기준**:
- [ ] Task가 Celery에 정상 등록됨
- [ ] Task 실행 시 집계가 정상 동작함
- [ ] 에러 발생 시 재시도 로직이 동작함

**예상 소요 시간**: 1시간

**파일 경로**:
- `apps/stocks/tasks.py`

---

### ☐ TODO #10: Celery Beat 스케줄 설정
**목표**: `config/settings/base.py` 또는 별도 설정 파일에 Beat 스케줄 추가

**상세 작업**:
1. CELERY_BEAT_SCHEDULE에 주봉 집계 추가
   ```python
   'aggregate-weekly-stock-prices': {
       'task': 'apps.stocks.tasks.aggregate_weekly_prices_task',
       'schedule': crontab(hour=1, minute=0, day_of_week=1),  # 매주 월요일 새벽 1시
   },
   ```

2. 월봉 집계 스케줄 추가
   ```python
   'aggregate-monthly-stock-prices': {
       'task': 'apps.stocks.tasks.aggregate_monthly_prices_task',
       'schedule': crontab(hour=2, minute=0, day_of_month=1),  # 매월 1일 새벽 2시
   },
   ```

3. 연봉 집계 스케줄 추가
   ```python
   'aggregate-yearly-stock-prices': {
       'task': 'apps.stocks.tasks.aggregate_yearly_prices_task',
       'schedule': crontab(hour=3, minute=0, day_of_month=1, month_of_year=1),  # 매년 1월 1일 새벽 3시
   },
   ```

4. 암호화폐 주봉/월봉 수집 스케줄 검토
   - 기존 `collect_crypto_candles_task`가 설정 기반으로 동작하므로, CoinCollectionConfig의 collection_interval에 따라 자동 실행됨
   - 필요 시 별도 스케줄 추가

**검증 기준**:
- [ ] Celery Beat 스케줄이 등록됨
- [ ] 스케줄 시간이 적절함
- [ ] Beat가 정상 동작함 (테스트 환경에서 수동 트리거)

**예상 소요 시간**: 30분

**파일 경로**:
- `config/settings/base.py`

**커밋 메시지**:
```
feat: Add Celery tasks for stock candle aggregation

- Add aggregate_weekly_prices_task for weekly aggregation
- Add aggregate_monthly_prices_task for monthly aggregation
- Add aggregate_yearly_prices_task for yearly aggregation
- Configure Celery Beat schedules for automatic aggregation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Phase 5: API 엔드포인트 추가

### ☐ TODO #11: 주식 API에 candle_type 파라미터 추가
**목표**: `api/v1/stocks.py`의 `/stocks/{stock_code}/prices` 엔드포인트에 candle_type 지원

**상세 작업**:
1. 엔드포인트 수정
   ```python
   @router.get("/{stock_code}/prices", response_model=List[DailyPriceResponse])
   async def get_stock_prices(
       stock_code: str,
       candle_type: str = Query(default="daily", enum=["daily", "weekly", "monthly", "yearly"]),
       start_date: Optional[date] = None,
       end_date: Optional[date] = None,
       limit: int = Query(default=30, le=365),
       current_user: User = Depends(get_current_user),
   ):
   ```

2. candle_type에 따라 다른 모델 조회
   ```python
   if candle_type == "daily":
       queryset = DailyPrice.objects.filter(stock=stock)
   elif candle_type == "weekly":
       queryset = WeeklyPrice.objects.filter(stock=stock)
   elif candle_type == "monthly":
       queryset = MonthlyPrice.objects.filter(stock=stock)
   elif candle_type == "yearly":
       queryset = YearlyPrice.objects.filter(stock=stock)
   ```

3. Schema 수정
   - `DailyPriceResponse`를 `PriceResponse`로 일반화하거나
   - candle_type별로 별도 response 사용

**검증 기준**:
- [ ] API 호출 시 candle_type 파라미터 동작함
- [ ] 각 candle_type별로 올바른 데이터 반환
- [ ] API 문서(Swagger)가 업데이트됨

**예상 소요 시간**: 45분

**파일 경로**:
- `api/v1/stocks.py`
- `api/schemas/daily_price.py` (필요 시 수정)

---

### ☐ TODO #12: 암호화폐 API 엔드포인트 추가
**목표**: `api/v1/crypto.py` 파일 생성 및 기본 CRUD 엔드포인트 추가

**상세 작업**:
1. `api/v1/crypto.py` 파일 생성

2. 코인 목록 조회 엔드포인트
   ```python
   @router.get("/", response_model=PaginatedResponse[CoinResponse])
   async def list_coins(...):
   ```

3. 특정 코인 조회
   ```python
   @router.get("/{market_code}", response_model=CoinResponse)
   async def read_coin(...):
   ```

4. 캔들 데이터 조회 (candle_type 지원)
   ```python
   @router.get("/{market_code}/candles", response_model=List[CoinCandleResponse])
   async def get_coin_candles(
       market_code: str,
       candle_type: str = Query(default="days", enum=["days", "weeks", "months"]),
       start_date: Optional[date] = None,
       end_date: Optional[date] = None,
       limit: int = Query(default=30, le=200),
       current_user: User = Depends(get_current_user),
   ):
   ```

5. Schema 추가 (`api/schemas/crypto.py`)
   - CoinResponse
   - CoinCandleResponse

6. main.py에 라우터 등록
   ```python
   from api.v1 import crypto
   app.include_router(crypto.router, prefix="/api/v1")
   ```

**검증 기준**:
- [ ] API 엔드포인트가 정상 동작함
- [ ] candle_type별로 올바른 데이터 반환
- [ ] Swagger 문서에 엔드포인트 표시됨

**예상 소요 시간**: 1.5시간

**파일 경로**:
- `api/v1/crypto.py` (신규)
- `api/schemas/crypto.py` (신규)
- `main.py`

**커밋 메시지**:
```
feat: Add multi-timeframe API endpoints

- Add candle_type parameter to stock prices endpoint
- Support daily/weekly/monthly/yearly candles for stocks
- Create crypto API endpoints with candle_type support
- Add CoinResponse and CoinCandleResponse schemas

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Phase 6: 테스트 작성

### ☐ TODO #13: 주식 집계 서비스 단위 테스트 작성
**목표**: `apps/stocks/tests/test_services.py`에 집계 함수 테스트 추가

**상세 작업**:
1. 테스트 데이터 준비 (Fixture)
   - 특정 주식에 대해 일봉 데이터 생성 (2주~1개월분)

2. `test_aggregate_weekly_prices()` 작성
   - 일봉 데이터를 주봉으로 집계
   - 집계 결과 검증 (시가, 고가, 저가, 종가, 거래량)

3. `test_aggregate_monthly_prices()` 작성
   - 일봉 데이터를 월봉으로 집계
   - 집계 결과 검증

4. `test_aggregate_yearly_prices()` 작성
   - 일봉 데이터를 연봉으로 집계
   - 집계 결과 검증

**검증 기준**:
- [ ] 모든 테스트가 통과함
- [ ] 집계 로직이 정확함
- [ ] Edge case 처리 확인 (주말, 휴일 등)

**예상 소요 시간**: 1.5시간

**파일 경로**:
- `apps/stocks/tests/test_services.py`

---

### ☐ TODO #14: 암호화폐 수집 서비스 테스트 검증
**목표**: `apps/crypto/tests/test_services.py`에 주봉/월봉 수집 테스트 추가

**상세 작업**:
1. 기존 `test_fetch_coin_candles()` 확인
   - candle_type='weeks' 테스트 추가
   - candle_type='months' 테스트 추가

2. Mock을 사용한 pyupbit API 테스트
   - pyupbit.get_ohlcv를 mock으로 대체
   - 주봉/월봉 데이터 반환 시뮬레이션

**검증 기준**:
- [ ] 주봉 수집 테스트 통과
- [ ] 월봉 수집 테스트 통과
- [ ] candle_type이 올바르게 저장됨

**예상 소요 시간**: 1시간

**파일 경로**:
- `apps/crypto/tests/test_services.py`

---

### ☐ TODO #15: API 엔드포인트 통합 테스트 작성
**목표**: `api/tests/test_stocks.py` 및 `api/tests/test_crypto.py`에 candle_type 파라미터 테스트 추가

**상세 작업**:
1. 주식 API 테스트 (`api/tests/test_stocks.py`)
   ```python
   def test_get_stock_prices_daily():
       response = client.get(f"/api/v1/stocks/{stock_code}/prices?candle_type=daily")
       assert response.status_code == 200

   def test_get_stock_prices_weekly():
       response = client.get(f"/api/v1/stocks/{stock_code}/prices?candle_type=weekly")
       assert response.status_code == 200
   ```

2. 암호화폐 API 테스트 (`api/tests/test_crypto.py` 신규 생성)
   ```python
   def test_get_coin_candles_days():
   def test_get_coin_candles_weeks():
   def test_get_coin_candles_months():
   ```

**검증 기준**:
- [ ] 모든 API 테스트 통과
- [ ] candle_type별로 올바른 데이터 반환 검증

**예상 소요 시간**: 1시간

**파일 경로**:
- `api/tests/test_stocks.py`
- `api/tests/test_crypto.py` (신규)

**커밋 메시지**:
```
test: Add comprehensive tests for multi-timeframe candles

- Add unit tests for stock candle aggregation services
- Add integration tests for crypto weekly/monthly collection
- Add API endpoint tests for candle_type parameter
- Verify OHLC calculation accuracy

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Phase 7: Admin UI 개선

### ☐ TODO #16: 주식 Admin에 주봉/월봉/연봉 표시 추가
**목표**: `apps/stocks/admin.py`에 WeeklyPrice, MonthlyPrice, YearlyPrice Admin 등록

**상세 작업**:
1. WeeklyPriceAdmin 클래스 생성
   ```python
   @admin.register(WeeklyPrice)
   class WeeklyPriceAdmin(admin.ModelAdmin):
       list_display = ['stock', 'trade_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
       list_filter = ['trade_date', 'stock__market']
       search_fields = ['stock__code', 'stock__name']
       readonly_fields = ['created_at', 'updated_at']
   ```

2. MonthlyPriceAdmin 생성 (동일 구조)
3. YearlyPriceAdmin 생성 (동일 구조)

4. 기존 StockAdmin에 Inline으로 추가 (선택사항)
   ```python
   class WeeklyPriceInline(admin.TabularInline):
       model = WeeklyPrice
       extra = 0
       max_num = 10
   ```

**검증 기준**:
- [ ] Admin UI에서 주봉/월봉/연봉 데이터 조회 가능
- [ ] 필터 및 검색 기능 동작
- [ ] Inline 표시 정상 (선택사항)

**예상 소요 시간**: 30분

**파일 경로**:
- `apps/stocks/admin.py`

---

### ☐ TODO #17: 암호화폐 Admin에 candle_type 필터 추가
**목표**: `apps/crypto/admin.py`의 CoinCandleAdmin에 candle_type 필터 추가

**상세 작업**:
1. CoinCandleAdmin 수정
   ```python
   @admin.register(CoinCandle)
   class CoinCandleAdmin(admin.ModelAdmin):
       list_display = ['coin', 'candle_type', 'trade_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
       list_filter = ['candle_type', 'trade_date', 'coin__market_code']
       search_fields = ['coin__market_code', 'coin__korean_name']
   ```

2. 재수집 액션에 candle_type 선택 추가 (선택사항)

**검증 기준**:
- [ ] Admin UI에서 candle_type 필터 동작
- [ ] 각 타입별로 데이터 조회 가능

**예상 소요 시간**: 15분

**파일 경로**:
- `apps/crypto/admin.py`

**커밋 메시지**:
```
feat: Enhance admin UI for multi-timeframe candles

- Register WeeklyPrice, MonthlyPrice, YearlyPrice in stock admin
- Add candle_type filter to CoinCandle admin
- Improve list display and search capabilities

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Phase 8: 문서 업데이트

### ☐ TODO #18: PROJECT_OVERVIEW.md 업데이트
**목표**: `docs/PROJECT_OVERVIEW.md`에 주/월/년 캔들 기능 문서화

**상세 작업**:
1. **데이터베이스 스키마** 섹션에 새 모델 추가
   - WeeklyPrice, MonthlyPrice, YearlyPrice 스키마 설명
   - CoinCandle의 candle_type 필드 설명

2. **API 엔드포인트** 섹션 업데이트
   - `/stocks/{stock_code}/prices?candle_type=` 파라미터 설명
   - `/crypto/{market_code}/candles?candle_type=` 엔드포인트 추가

3. **Celery 태스크** 섹션에 새 태스크 추가
   - aggregate_weekly_prices_task
   - aggregate_monthly_prices_task
   - aggregate_yearly_prices_task
   - Celery Beat 스케줄 설명

4. **사용 예시** 섹션 추가
   ```markdown
   ### 주봉 데이터 조회
   GET /api/v1/stocks/005930/prices?candle_type=weekly&limit=52
   ```

**검증 기준**:
- [ ] 모든 새 기능이 문서화됨
- [ ] API 예시가 정확함
- [ ] 마크다운 형식이 올바름

**예상 소요 시간**: 1시간

**파일 경로**:
- `docs/PROJECT_OVERVIEW.md`

---

### ☐ TODO #19: README.md 업데이트 (선택사항)
**목표**: 프로젝트 루트의 README.md에 주요 기능 추가

**상세 작업**:
1. Features 섹션에 추가
   ```markdown
   - ✅ 다중 시간대 캔들 지원 (일봉/주봉/월봉/연봉)
   - ✅ 주식 일봉 데이터 자동 집계로 주/월/연봉 생성
   - ✅ 암호화폐 주봉/월봉 직접 수집 (pyupbit API)
   ```

2. API 사용 예시 추가

**검증 기준**:
- [ ] README가 최신 기능 반영
- [ ] 사용자가 이해하기 쉬움

**예상 소요 시간**: 30분

**파일 경로**:
- `README.md`

**커밋 메시지**:
```
docs: Update documentation for multi-timeframe candle feature

- Document WeeklyPrice, MonthlyPrice, YearlyPrice models
- Add API endpoint examples for candle_type parameter
- Document Celery tasks for automatic aggregation
- Update README with new features

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Phase 9: 초기 데이터 집계 및 검증

### ☐ TODO #20: 기존 일봉 데이터를 주/월/연봉으로 집계
**목표**: 운영 환경에서 히스토리 데이터를 집계하는 관리 커맨드 작성

**상세 작업**:
1. Django Management Command 생성
   ```bash
   python manage.py makemigrations stocks
   ```
   파일: `apps/stocks/management/commands/aggregate_historical_candles.py`

2. Command 구현
   ```python
   class Command(BaseCommand):
       help = 'Aggregate historical daily prices into weekly/monthly/yearly candles'

       def add_arguments(self, parser):
           parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
           parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
           parser.add_argument('--stock-code', type=str, help='Specific stock code')

       def handle(self, *args, **options):
           # 모든 주식 또는 특정 주식에 대해
           # aggregate_weekly_prices()
           # aggregate_monthly_prices()
           # aggregate_yearly_prices() 호출
   ```

3. 실행 및 검증
   ```bash
   python manage.py aggregate_historical_candles --start-date=2020-01-01 --end-date=2025-12-09
   ```

**검증 기준**:
- [ ] 커맨드가 정상 실행됨
- [ ] 모든 주식의 히스토리 데이터가 집계됨
- [ ] 데이터 무결성 확인 (샘플 검증)

**예상 소요 시간**: 1시간

**파일 경로**:
- `apps/stocks/management/commands/aggregate_historical_candles.py`

---

### ☐ TODO #21: 암호화폐 주봉/월봉 수집 설정 생성 및 실행
**목표**: Admin에서 주봉/월봉 수집 설정을 생성하고 초기 데이터 수집

**상세 작업**:
1. Admin UI에서 CoinCollectionConfig 생성
   - 주봉 설정: candle_type='weeks', collection_interval='weekly', period_days=200
   - 월봉 설정: candle_type='months', collection_interval='monthly', period_days=200

2. Celery Task 수동 실행
   ```python
   from apps.crypto.tasks import collect_crypto_candles_task
   collect_crypto_candles_task.delay()
   ```

3. 데이터 검증
   - CoinCandle 테이블에서 candle_type='weeks', 'months' 데이터 확인
   - 샘플 데이터의 OHLC 값 검증

**검증 기준**:
- [ ] 주봉 데이터가 수집됨
- [ ] 월봉 데이터가 수집됨
- [ ] 데이터가 정확함

**예상 소요 시간**: 30분

**파일 경로**:
- Admin UI
- Celery 로그

**커밋 메시지**:
```
feat: Add management command for historical candle aggregation

- Create aggregate_historical_candles command for stocks
- Support date range and specific stock filtering
- Enable bulk aggregation for weekly/monthly/yearly candles

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Phase 10: PR 생성

### ☐ TODO #22: 브랜치 생성 및 작업 커밋 정리
**목표**: 작업 브랜치 생성 및 모든 변경사항 커밋

**상세 작업**:
1. 브랜치 생성
   ```bash
   git checkout -b asset-backend/multi-timeframe-candles
   ```

2. 모든 변경사항 확인
   ```bash
   git status
   git diff
   ```

3. 각 Phase별로 커밋 생성 (이미 Phase별로 커밋 메시지 정의됨)
   - Phase 1: 모델 추가 및 마이그레이션
   - Phase 2: 주식 집계 서비스
   - Phase 3: 암호화폐 수집 서비스
   - Phase 4: Celery 태스크
   - Phase 5: API 엔드포인트
   - Phase 6: 테스트
   - Phase 7: Admin UI
   - Phase 8: 문서
   - Phase 9: 초기 데이터

**검증 기준**:
- [ ] 모든 변경사항이 커밋됨
- [ ] 커밋 메시지가 명확함
- [ ] 커밋이 논리적으로 그룹화됨

**예상 소요 시간**: 30분

---

### ☐ TODO #23: PR 생성 및 설명 작성
**목표**: GitHub PR 생성

**상세 작업**:
1. 브랜치 푸시
   ```bash
   git push -u origin asset-backend/multi-timeframe-candles
   ```

2. PR 생성
   ```bash
   gh pr create --title "feat: Add multi-timeframe candle support (daily/weekly/monthly/yearly)" --body "$(cat <<'EOF'
   ## Summary
   - 주식 및 암호화폐 데이터에 다중 시간대 캔들(일봉/주봉/월봉/연봉) 지원 추가
   - 주식: 일봉 데이터를 집계하여 주봉/월봉/연봉 생성
   - 암호화폐: pyupbit API로 주봉/월봉 직접 수집
   - API 엔드포인트에 candle_type 파라미터 추가
   - Celery Task를 통한 자동 집계 및 수집

   ## Changes
   ### Database
   - Add WeeklyPrice, MonthlyPrice, YearlyPrice models for stocks
   - Extend CoinCandle with candle_type field for crypto

   ### Services
   - Implement aggregate_weekly_prices(), aggregate_monthly_prices(), aggregate_yearly_prices()
   - Enable weekly/monthly collection in fetch_coin_candles()

   ### API
   - Add candle_type parameter to /stocks/{stock_code}/prices
   - Create /crypto/{market_code}/candles endpoint

   ### Tasks
   - Add Celery tasks for stock candle aggregation
   - Configure Celery Beat schedules

   ### Tests
   - Add unit tests for aggregation services
   - Add integration tests for API endpoints

   ## Test plan
   - [ ] Run all unit tests: pytest apps/stocks/tests apps/crypto/tests
   - [ ] Run API tests: pytest api/tests
   - [ ] Test Celery tasks manually
   - [ ] Verify Admin UI functionality
   - [ ] Test historical data aggregation command
   - [ ] Verify API responses for different candle_type values

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

**검증 기준**:
- [ ] PR이 생성됨
- [ ] PR 설명이 명확함
- [ ] 체크리스트가 포함됨

**예상 소요 시간**: 15분

**커밋 메시지**:
```
(PR 생성 - 커밋 없음)
```

---

# 작업 완료 체크리스트

## Phase별 완료 현황
- [ ] Phase 1: 데이터베이스 스키마 설계 및 마이그레이션
- [ ] Phase 2: 주식 캔들 집계 서비스 구현
- [ ] Phase 3: 암호화폐 주봉/월봉 수집 서비스 구현
- [ ] Phase 4: Celery Task 추가
- [ ] Phase 5: API 엔드포인트 추가
- [ ] Phase 6: 테스트 작성
- [ ] Phase 7: Admin UI 개선
- [ ] Phase 8: 문서 업데이트
- [ ] Phase 9: 초기 데이터 집계 및 검증
- [ ] Phase 10: PR 생성

## 최종 검증
- [ ] 모든 테스트 통과
- [ ] API 문서(Swagger) 업데이트 확인
- [ ] 문서 완전성 검토
- [ ] PR 생성 완료
- [ ] PROJECT_OVERVIEW.md 최신화

# 참고 자료

## pykrx API
- 일봉만 제공: `get_market_ohlcv_by_ticker(date, market="ALL")`
- 주봉/월봉은 일봉 집계로 생성 필요

## pyupbit API
- 다중 시간대 지원: `get_ohlcv(ticker, interval='days'|'weeks'|'months', count, to)`
- 최대 200개까지 조회 가능

## Django ORM Aggregation
```python
from django.db.models.functions import TruncWeek, TruncMonth, TruncYear
from django.db.models import Min, Max, Sum

# 주봉 집계 예시
weekly_data = DailyPrice.objects.filter(
    stock=stock,
    trade_date__range=(start_date, end_date)
).annotate(
    week=TruncWeek('trade_date')
).values('week').annotate(
    open_price=Min('open_price', filter=Q(trade_date=Min('trade_date'))),
    high_price=Max('high_price'),
    low_price=Min('low_price'),
    close_price=Max('close_price', filter=Q(trade_date=Max('trade_date'))),
    volume=Sum('volume')
)
```

# Notepad (중요한 발견사항 기록)

## 발견사항 1: 암호화폐는 이미 주봉/월봉 인프라가 준비됨
- `CoinCollectionConfig` 모델에 'weeks', 'months' candle_type이 이미 정의됨
- `fetch_coin_candles()` 함수도 candle_type 파라미터를 지원함
- 하지만 실제로 'days'만 사용 중
- **결론**: 암호화폐는 활성화만 하면 됨 (새 코드 작성 최소화)

## 발견사항 2: 주식은 pykrx API 제약으로 일봉만 수집 가능
- pykrx는 일봉 데이터만 제공
- 주봉/월봉/연봉은 일봉 데이터를 집계하여 생성해야 함
- Django ORM의 Trunc 함수를 사용한 집계 필요

## 발견사항 3: 암호화폐 API 엔드포인트가 없음
- 주식 API는 `/stocks/{stock_code}/prices` 존재
- 암호화폐 API는 아직 구현되지 않음
- **결론**: crypto API 엔드포인트를 새로 생성해야 함

## 발견사항 4: 기존 ai-todolist.md가 매우 크다
- 파일 크기가 28480 토큰으로 Read tool 제한(25000 토큰) 초과
- 이전 작업(암호화폐 기능 추가)의 완료된 TODO가 대량 포함됨
- **결론**: 새 작업 계획으로 파일 덮어쓰기 완료 (백업은 ai-todolist-backup.md에 저장)
