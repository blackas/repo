# 아키텍처 문서

KStock Reporter 시스템 아키텍처 문서입니다.

## 시스템 개요

KStock Reporter는 한국 주식 시장 데이터를 수집하고, 사용자별 관심종목 기반 리포트를 생성하여 카카오 알림톡으로 발송하는 시스템입니다.

## 기술 스택

### Backend
- **Django 5.1**: Admin, ORM, 마이그레이션
- **FastAPI 0.115**: REST API, 자동 문서화
- **Python 3.11+**: 애플리케이션 언어

### Database
- **PostgreSQL 16**: 메인 데이터베이스
- **Redis 7**: 캐싱, 메시지 브로커

### Task Queue
- **Celery 5.4**: 비동기 작업 처리
- **Celery Beat**: 스케줄링

### Monitoring
- **Sentry**: 에러 추적
- **Flower**: Celery 모니터링

### Deployment
- **Docker**: 컨테이너화
- **Docker Compose**: 오케스트레이션
- **Gunicorn**: WSGI 서버
- **Uvicorn**: ASGI 서버

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                         클라이언트                            │
├─────────────────────────────────────────────────────────────┤
│  Web Browser  │  Mobile App  │  API Client  │  curl/httpx  │
└────────┬─────────────┬─────────────┬───────────────┬────────┘
         │             │             │               │
         ├─────────────┴─────────────┴───────────────┤
         │                                           │
┌────────▼───────────────────────────────────────────▼────────┐
│                    Nginx (Reverse Proxy)                     │
│                     SSL Termination                          │
└────────┬────────────────────────────────────────┬────────────┘
         │                                        │
┌────────▼────────┐                      ┌───────▼────────────┐
│  Django (8000)  │                      │  FastAPI (8001)    │
│  - Admin Panel  │                      │  - REST API        │
│  - ORM          │                      │  - JWT Auth        │
│  - Migrations   │                      │  - Auto Docs       │
└────────┬────────┘                      └───────┬────────────┘
         │                                       │
         └───────────────┬───────────────────────┘
                         │
         ┌───────────────▼────────────────┐
         │       PostgreSQL (5432)        │
         │    - Users, Stocks, Reports    │
         └────────────────────────────────┘
                         │
         ┌───────────────▼────────────────┐
         │         Redis (6379)           │
         │  - Cache (DB 2)                │
         │  - Celery Broker (DB 0)        │
         │  - Celery Results (DB 1)       │
         │  - Rate Limiting (DB 3)        │
         └───────────┬────────────────────┘
                     │
         ┌───────────▼────────────────┐
         │   Celery Worker & Beat     │
         │  - Stock Data Sync         │
         │  - Report Generation       │
         │  - Notification Sending    │
         └───────────┬────────────────┘
                     │
         ┌───────────▼────────────────┐
         │   External Services        │
         │  - KRX API (pykrx)         │
         │  - Kakao Alimtalk API      │
         │  - Sentry                  │
         └────────────────────────────┘
```

## 데이터 흐름

### 1. 주식 데이터 수집 플로우

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Celery   │────>│ KRX API  │────>│ Django   │────>│Postgre   │
│ Beat     │     │ (pykrx)  │     │ ORM      │     │SQL       │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
   │ 07:00                              │
   │ Scheduled                          │
   └────────────────────────────────────┘
         Stock Data Sync Task
```

### 2. 리포트 생성 플로우

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Celery   │────>│ Django   │────>│ Report   │────>│Postgre   │
│ Beat     │     │ Service  │     │ Model    │     │SQL       │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
   │ 07:30              │
   │ Scheduled          ├─> Watchlist Query
   └────────────────────┘
         Report Generation Task
```

### 3. 알림 발송 플로우

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Celery   │────>│ Kakao    │────>│ Notif.   │────>│Postgre   │
│ Beat     │     │ Client   │     │ Log      │     │SQL       │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
   │ 08:00              │
   │ Scheduled          └─> Kakao Alimtalk API
   └────────────────────────────────────────────────┘
         Notification Sending Task
```

### 4. API 요청 플로우

```
┌─────────┐  JWT  ┌─────────┐  Query ┌─────────┐  Cache ┌─────┐
│ Client  │──────>│FastAPI  │───────>│ Django  │───────>│Redis│
└─────────┘       │ Router  │        │  ORM    │        └─────┘
                  └─────────┘        └─────────┘           │
                       │                   │                │
                       │                   ▼                │
                       │             ┌─────────┐            │
                       │             │Postgre  │◀───────────┘
                       │             │SQL      │  DB Query
                       │             └─────────┘
                       ▼
                  JSON Response
```

## 데이터베이스 스키마

### accounts 앱

```sql
-- User (Django 기본 User 확장)
User
  - id: BigAutoField (PK)
  - username: CharField (unique, indexed)
  - email: EmailField
  - phone_number: CharField (indexed)
  - kakao_user_id: CharField
  - receive_daily_report: BooleanField

-- WatchList
WatchList
  - id: BigAutoField (PK)
  - user_id: FK(User)
  - name: CharField
  - created_at: DateTimeField
  INDEX: (user_id, created_at DESC)

-- WatchListItem
WatchListItem
  - id: BigAutoField (PK)
  - watchlist_id: FK(WatchList)
  - stock_id: FK(Stock)
  UNIQUE: (watchlist_id, stock_id)
```

### stocks 앱

```sql
-- Stock
Stock
  - id: BigAutoField (PK)
  - code: CharField (unique, 6자리)
  - name: CharField (indexed)
  - market: CharField (indexed)
  - sector: CharField
  - listed_at: DateField
  - is_active: BooleanField

-- DailyPrice
DailyPrice
  - id: BigAutoField (PK)
  - stock_id: FK(Stock)
  - trade_date: DateField (indexed)
  - open_price: DecimalField
  - high_price: DecimalField
  - low_price: DecimalField
  - close_price: DecimalField
  - volume: BigIntegerField
  - amount: BigIntegerField
  - change: DecimalField
  - change_rate: DecimalField
  - market_cap: BigIntegerField
  UNIQUE: (stock_id, trade_date)
  INDEX: (trade_date, change_rate DESC)
  INDEX: (stock_id, trade_date)
```

### reports 앱

```sql
-- DailyReport
DailyReport
  - id: BigAutoField (PK)
  - user_id: FK(User)
  - report_date: DateField
  - title: CharField
  - body_text: TextField
  - created_at: DateTimeField
  UNIQUE: (user_id, report_date)
  INDEX: (user_id, report_date DESC)
  INDEX: (created_at DESC)
```

### notifications 앱

```sql
-- NotificationLog
NotificationLog
  - id: BigAutoField (PK)
  - user_id: FK(User)
  - channel: CharField (choices: kakao)
  - message: TextField
  - sent_at: DateTimeField
  - success: BooleanField
  - response_code: CharField
  - response_body: TextField
```

## API 엔드포인트

### 인증 (Authentication)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/v1/auth/register | 회원가입 | No |
| POST | /api/v1/auth/login | 로그인 (JWT 발급) | No |

### 사용자 (Users)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/v1/users/me | 현재 사용자 정보 | Yes |
| PUT | /api/v1/users/me | 사용자 정보 수정 | Yes |
| GET | /api/v1/users/ | 사용자 목록 | Admin |
| GET | /api/v1/users/{id} | 특정 사용자 조회 | Admin |

### 주식 (Stocks)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/v1/stocks/ | 주식 목록 | Yes |
| GET | /api/v1/stocks/{code} | 주식 상세 | Yes |
| POST | /api/v1/stocks/ | 주식 생성 | Admin |
| PUT | /api/v1/stocks/{code} | 주식 수정 | Admin |
| GET | /api/v1/stocks/{code}/prices | 주식 가격 데이터 | Yes |

### 관심목록 (Watchlists)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/v1/watchlists/ | 관심목록 조회 | Yes |
| POST | /api/v1/watchlists/ | 관심목록 생성 | Yes |
| GET | /api/v1/watchlists/{id} | 특정 관심목록 조회 | Yes |
| PUT | /api/v1/watchlists/{id} | 관심목록 수정 | Yes |
| DELETE | /api/v1/watchlists/{id} | 관심목록 삭제 | Yes |
| POST | /api/v1/watchlists/{id}/items | 종목 추가 | Yes |
| DELETE | /api/v1/watchlists/{id}/items/{item_id} | 종목 제거 | Yes |

### 리포트 (Reports)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/v1/reports/ | 리포트 목록 | Yes |
| GET | /api/v1/reports/{id} | 리포트 상세 | Yes |
| GET | /api/v1/reports/date/{date} | 특정 날짜 리포트 | Yes |

## 보안

### 인증 및 인가

- **JWT (JSON Web Token)**
  - 24시간 유효 기간
  - HS256 알고리즘
  - Bearer 토큰 방식

- **비밀번호 해싱**
  - Django의 PBKDF2 알고리즘
  - 최소 8자 이상

### Rate Limiting

- **일반 사용자**: 100 req/min, 1000 req/hour
- **인증 엔드포인트**: 5-10 req/min
- **조회 엔드포인트**: 100 req/min
- **쓰기 엔드포인트**: 50 req/min

### CORS

- 개발: 모든 origin 허용
- 운영: 특정 도메인만 허용

### HTTPS

- Let's Encrypt SSL 인증서
- HSTS 설정 (1년)
- 모든 HTTP 요청 HTTPS로 리다이렉트

## 성능 최적화

### 데이터베이스 최적화

1. **인덱스**
   - 자주 조회되는 필드에 인덱스 추가
   - 복합 인덱스 활용

2. **쿼리 최적화**
   - select_related() - ForeignKey
   - prefetch_related() - ManyToMany
   - only() / defer() - 필요한 필드만

3. **커넥션 풀**
   - CONN_MAX_AGE 설정
   - 재사용 가능한 연결 유지

### 캐싱 전략

1. **Redis 캐싱**
   - 주식 데이터: 15분
   - 관심목록: 5분
   - 리포트: 1시간

2. **쿼리 캐싱**
   - Django ORM 캐싱
   - 결과 캐싱

### 비동기 처리

- Celery를 통한 무거운 작업 비동기 처리
- 데이터 수집, 리포트 생성, 알림 발송

## 모니터링

### 로그

- **Django 로그**: logs/django.log
- **에러 로그**: logs/error.log
- **Celery 로그**: logs/celery.log
- **주식 데이터 로그**: logs/stocks.log

### 메트릭

- **Sentry**: 에러 추적, 성능 모니터링
- **Flower**: Celery 작업 모니터링
- **PostgreSQL**: 쿼리 성능

## 스케일링 전략

### 수평 스케일링

1. **API 서버**: 여러 인스턴스 실행
2. **Celery Worker**: 워커 수 증가
3. **로드 밸런서**: Nginx, AWS ALB

### 수직 스케일링

1. **CPU**: 워커 수 증가
2. **메모리**: 캐시 크기 증가
3. **디스크**: SSD 사용

### 데이터베이스 스케일링

1. **읽기 복제본**: PostgreSQL Read Replica
2. **샤딩**: 시간 기반 파티셔닝
3. **아카이빙**: 오래된 데이터 별도 저장

## 재해 복구

### 백업

- **데이터베이스**: 매일 자동 백업
- **로그**: 7일 보관
- **설정 파일**: Git 버전 관리

### 복구 절차

1. 최신 백업에서 데이터베이스 복원
2. 컨테이너 재시작
3. 마이그레이션 실행
4. 서비스 헬스 체크

## 개발 환경

### 로컬 개발

```bash
python manage.py runserver         # Django (8000)
uvicorn main:app --reload          # FastAPI (8001)
celery -A config worker -l info    # Celery Worker
celery -A config beat -l info      # Celery Beat
```

### Docker 개발

```bash
docker-compose up -d
docker-compose logs -f
```

### 테스트

```bash
pytest                              # 전체 테스트
pytest --cov=apps                   # 커버리지
black .                             # 코드 포맷
flake8 .                            # 린팅
```

## 참고 자료

- [Django 공식 문서](https://docs.djangoproject.com/)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Celery 공식 문서](https://docs.celeryq.dev/)
- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)
