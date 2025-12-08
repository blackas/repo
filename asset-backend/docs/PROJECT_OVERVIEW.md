# Asset Backend 프로젝트 문서

**프로젝트명**: Asset Backend (구 KStock Reporter)
**마지막 업데이트**: 2025-12-09
**현재 브랜치**: asset-backend/login

---

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [기술 스택](#기술-스택)
3. [시스템 아키텍처](#시스템-아키텍처)
4. [주요 기능](#주요-기능)
5. [API 엔드포인트](#api-엔드포인트)
6. [인증 시스템](#인증-시스템)
7. [데이터베이스 스키마](#데이터베이스-스키마)
8. [개발 이력](#개발-이력)
9. [배포 가이드](#배포-가이드)

---

## 프로젝트 개요

Asset Backend는 Django와 FastAPI를 결합한 하이브리드 백엔드 시스템입니다. 한국 주식과 암호화폐 데이터를 수집하고, 사용자별 관심종목 기반 리포트를 생성하여 카카오 알림톡으로 발송하는 시스템입니다.

### 핵심 목표
- **데이터 수집**: KRX(한국거래소) 및 Upbit API를 통한 실시간 데이터 수집
- **자동화**: Celery를 통한 스케줄링 자동 작업 수행
- **확장성**: Django Admin + FastAPI REST API로 다양한 클라이언트 지원
- **표준 준수**: OAuth 2.0 기반 인증으로 향후 Keycloak 마이그레이션 대비

### 프로젝트 히스토리
- **이전 이름**: KStock Reporter
- **현재 이름**: Asset Backend (암호화폐 기능 추가)
- **주요 리팩토링**: 2025-11-25 (Phase 1-3 완료)
- **OAuth 2.0 인증 도입**: 2025-12-04

---

## 기술 스택

### Backend Framework
- **Django 5.1**: Admin 인터페이스, ORM, 마이그레이션 관리
- **FastAPI 0.122.0**: 고성능 REST API, 자동 문서화 (Swagger/ReDoc)
- **Python 3.11+**: 애플리케이션 언어

### Database
- **PostgreSQL 16**: 메인 데이터베이스
- **Redis 7**:
  - DB 0: Celery Broker
  - DB 1: Celery Results
  - DB 2: Django Cache
  - DB 3: Rate Limiting

### Task Queue & Scheduling
- **Celery 5.5.3**: 비동기 작업 처리
- **Celery Beat**: 스케줄링
- **Flower 2.0.1**: Celery 모니터링 대시보드

### 데이터 소스
- **pykrx 1.0.51**: KRX(한국거래소) 주식 데이터
- **pyupbit 0.2.31**: Upbit 암호화폐 데이터

### Authentication & Security
- **OAuth 2.0 (RFC 6749)**: Password Grant, Refresh Token Grant
- **JWT**: JSON Web Token (python-jose)
- **slowapi 0.1.9**: API Rate Limiting

### Monitoring & Error Tracking
- **Sentry 2.18.0**: 에러 추적 및 성능 모니터링
- **django-prometheus 2.3.1**: 메트릭 수집

### Testing & Code Quality
- **pytest 9.0.1**: 테스트 프레임워크
- **pytest-asyncio 1.3.0**: 비동기 테스트
- **black, flake8, mypy**: 코드 품질 도구

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    클라이언트 레이어                          │
├─────────────────────────────────────────────────────────────┤
│  Web Browser  │  Mobile App  │  API Client  │  curl/httpx  │
└────────┬─────────────┬─────────────┬───────────────┬────────┘
         │             │             │               │
         └─────────────┴─────────────┴───────────────┘
                         │
         ┌───────────────▼────────────────────────────┐
         │        Nginx (Reverse Proxy)               │
         │            SSL Termination                 │
         └───────┬───────────────────────┬────────────┘
                 │                       │
    ┌────────────▼──────────┐  ┌────────▼───────────────┐
    │  Django (8000)        │  │  FastAPI (8001)        │
    │  - Admin Panel        │  │  - REST API            │
    │  - ORM                │  │  - OAuth 2.0 Auth      │
    │  - Migrations         │  │  - Auto Docs (Swagger) │
    └────────┬──────────────┘  └────────┬───────────────┘
             │                          │
             └──────────┬───────────────┘
                        │
        ┌───────────────▼────────────────┐
        │       PostgreSQL (5432)        │
        │    - Users, Stocks, Crypto     │
        │    - Reports, Notifications    │
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
        │  - Crypto Data Sync (NEW)  │
        │  - Report Generation       │
        │  - Notification Sending    │
        └───────────┬────────────────┘
                    │
        ┌───────────▼────────────────┐
        │   External Services        │
        │  - KRX API (pykrx)         │
        │  - Upbit API (pyupbit)     │
        │  - Kakao Alimtalk API      │
        │  - Sentry                  │
        └────────────────────────────┘
```

---

## 주요 기능

### 1. 주식 데이터 관리
- **종목 마스터 관리**: KRX에서 상장 종목 정보 자동 동기화
- **일별 시세 수집**: 시가, 고가, 저가, 종가, 거래량 데이터 수집
- **스케줄**: 매일 07:00 종목 동기화, 07:20 일별 시세 수집

### 2. 암호화폐 데이터 관리 ⭐ NEW
- **코인 마스터 관리**: Upbit KRW 마켓 코인 목록 자동 동기화
- **일봉 캔들 데이터**: OHLCV (시가, 고가, 저가, 종가, 거래량) 수집
- **수집 설정 관리**: 코인별, 기간별 수집 설정 가능 (최대 200일)
- **스케줄**: 매일 07:10 코인 마스터, 07:15 캔들 데이터
- **Rate Limiting**: 초당 6.7회 요청 제한 (Upbit API 준수)

### 3. 사용자 관심종목 관리
- **WatchList**: 사용자별 여러 관심목록 생성 가능
- **WatchListItem**: 관심목록에 종목 추가/제거
- **중복 방지**: 동일 관심목록 내 종목 중복 불가

### 4. 일일 리포트 생성
- **자동 생성**: 매일 07:30 수신 설정 사용자 대상
- **내용**: 관심종목 중 상승률/하락률 TOP 3
- **저장**: DailyReport 모델에 텍스트 저장

### 5. 카카오 알림톡 발송
- **자동 발송**: 매일 08:00 리포트 발송
- **로그 관리**: NotificationLog에 성공/실패 기록
- **재시도**: 실패 시 2회 재시도

### 6. OAuth 2.0 인증 ⭐ NEW
- **지원 Grant Type**:
  - Password Grant: 사용자명/비밀번호 로그인
  - Refresh Token Grant: Access Token 갱신
- **엔드포인트**:
  - `/auth/token`: 토큰 발급 및 갱신
  - `/auth/revoke`: Refresh Token 무효화
  - `/auth/userinfo`: 현재 사용자 정보 (OIDC 호환)
  - `/auth/logout`: 모든 토큰 무효화
- **향후 계획**: Keycloak 마이그레이션 준비

---

## API 엔드포인트

### 인증 (Authentication)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/v1/auth/token | 토큰 발급/갱신 (OAuth 2.0) | No |
| POST | /api/v1/auth/revoke | Refresh Token 무효화 | No |
| GET | /api/v1/auth/userinfo | 현재 사용자 정보 (OIDC) | Yes |
| POST | /api/v1/auth/logout | 로그아웃 (모든 토큰 무효화) | Yes |
| POST | /api/v1/auth/register | 회원가입 | No |
| POST | /api/v1/auth/login | 레거시 로그인 (deprecated) | No |

### 사용자 (Users)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/v1/users/me | 현재 사용자 정보 | Yes |
| PUT | /api/v1/users/me | 사용자 정보 수정 | Yes |

### 주식 (Stocks)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/v1/stocks/ | 주식 목록 (검색, 필터링) | Yes |
| GET | /api/v1/stocks/{code} | 주식 상세 | Yes |
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

### API 문서
- **Swagger UI**: http://localhost:8001/api/docs
- **ReDoc**: http://localhost:8001/api/redoc

---

## 인증 시스템

### OAuth 2.0 Token Endpoint

#### Password Grant (로그인)
```bash
POST /api/v1/auth/token
Content-Type: application/json

{
  "grant_type": "password",
  "username": "user@example.com",
  "password": "your-password",
  "device_type": "web",  # optional: web, ios, android
  "device_id": "unique-device-id"  # optional
}

# Response
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_expires_in": 2592000
}
```

#### Refresh Token Grant (토큰 갱신)
```bash
POST /api/v1/auth/token
Content-Type: application/json

{
  "grant_type": "refresh_token",
  "refresh_token": "eyJ..."
}

# Response
{
  "access_token": "eyJ...",  # 새 Access Token
  "refresh_token": "eyJ...",  # 기존 Refresh Token 재사용
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_expires_in": 2591000  # 남은 유효 시간
}
```

#### Token Revocation (토큰 무효화)
```bash
POST /api/v1/auth/revoke
Content-Type: application/json

{
  "token": "eyJ...",
  "token_type_hint": "refresh_token"  # optional
}
```

### 토큰 관리
- **Access Token**: 1시간 유효
- **Refresh Token**: 30일 유효
- **저장 위치**: PostgreSQL (RefreshToken 모델)
- **Device Tracking**: device_type, device_id로 디바이스별 관리
- **Logout**: 사용자의 모든 Refresh Token 무효화

### 보안 고려사항
- Refresh Token은 DB에 암호화 저장
- Device별 토큰 관리로 디바이스별 로그아웃 가능
- Token Rotation 정책 (향후 구현 고려)
- Keycloak 마이그레이션을 위한 표준 준수 설계

---

## 데이터베이스 스키마

### accounts 앱

#### User (Django 기본 User 확장)
```sql
- id: BigAutoField (PK)
- username: CharField (unique, indexed)
- email: EmailField
- phone_number: CharField (indexed)
- receive_daily_report: BooleanField
```

#### RefreshToken ⭐ NEW
```sql
- id: BigAutoField (PK)
- user_id: FK(User)
- token: TextField (unique, encrypted)
- device_type: CharField(10)  # web, ios, android
- device_id: CharField(255)
- expires_at: DateTimeField
- created_at: DateTimeField
- revoked: BooleanField
INDEX: (user_id, device_type, revoked)
INDEX: (token) unique
```

#### WatchList
```sql
- id: BigAutoField (PK)
- user_id: FK(User)
- name: CharField
- created_at: DateTimeField
INDEX: (user_id, created_at DESC)
```

#### WatchListItem
```sql
- id: BigAutoField (PK)
- watchlist_id: FK(WatchList)
- stock_id: FK(Stock)
UNIQUE: (watchlist_id, stock_id)
```

### stocks 앱

#### Stock (주식 종목)
```sql
- id: BigAutoField (PK)
- code: CharField (unique, 6자리)
- name: CharField (indexed)
- market: CharField (indexed)  # KOSPI, KOSDAQ
- sector: CharField
- listed_at: DateField
- is_active: BooleanField
```

#### DailyPrice (일별 주가)
```sql
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

### crypto 앱 ⭐ NEW

#### Coin (암호화폐 마스터)
```sql
- id: BigAutoField (PK)
- market_code: CharField(20) (unique)  # KRW-BTC
- korean_name: CharField(100)
- english_name: CharField(100)
- is_active: BooleanField
- created_at: DateTimeField
- updated_at: DateTimeField
INDEX: market_code (unique)
```

#### CoinCandle (일봉 캔들)
```sql
- id: BigAutoField (PK)
- coin_id: FK(Coin)
- trade_date: DateField
- open_price: DecimalField(20,8)
- high_price: DecimalField(20,8)
- low_price: DecimalField(20,8)
- close_price: DecimalField(20,8)
- volume: DecimalField(20,8)  # 코인 거래량
- candle_acc_trade_volume: DecimalField(20,2)  # KRW 거래대금
- created_at: DateTimeField
- updated_at: DateTimeField
UNIQUE: (coin_id, trade_date)
INDEX: (coin_id, -trade_date)
```

#### CoinCollectionConfig (수집 설정)
```sql
- id: BigAutoField (PK)
- name: CharField(100) (unique)
- candle_type: CharField(20)  # days, minutes, weeks, months
- collection_interval: CharField(20)  # hourly, daily, weekly
- period_days: Integer (1-200)
- is_active: BooleanField
- coins: ManyToMany(Coin)
- created_at: DateTimeField
- updated_at: DateTimeField
```

### reports 앱

#### DailyReport
```sql
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

#### NotificationLog
```sql
- id: BigAutoField (PK)
- user_id: FK(User)
- channel: CharField (choices: kakao)
- message: TextField
- sent_at: DateTimeField
- success: BooleanField
- response_code: CharField
- response_body: TextField
```

---

## 개발 이력

### Phase 1: 필수 인프라 구축 (2025-11-25)
✅ Django Admin 인터페이스 추가 (4개 앱)
✅ pytest 테스트 인프라 구축
✅ 로깅 시스템 설정 (파일별 로그)
✅ 환경별 설정 분리 (dev, prod, test)
✅ Common 앱 (유틸리티, 예외, 검증)
✅ 보안 설정 강화

**생성 파일**: 33개

### Phase 2: FastAPI 통합 및 성능 개선 (2025-11-25)
✅ FastAPI 통합 (Django와 공존)
✅ Pydantic 스키마 (자동 검증)
✅ REST API 엔드포인트 (CRUD)
✅ JWT 인증 시스템
✅ Redis 캐싱 전략
✅ 서비스 레이어 에러 처리

**생성 파일**: 19개

### Phase 3: CI/CD 및 운영 도구 (2025-11-25)
✅ GitHub Actions CI/CD (lint, test, build, deploy)
✅ Celery Flower 모니터링
✅ Sentry 에러 추적 (Django + FastAPI)
✅ 데이터베이스 최적화 (인덱스, 커스텀 매니저)
✅ API Rate Limiting (Redis 기반)
✅ 포괄적인 문서화 (배포, 아키텍처)

**생성 파일**: 12개

### Phase 4: 실제 동작 검증 및 누락 구현 (2025-11-27)
✅ API 테스트 코드 작성 (httpx)
✅ Celery 태스크 에러 처리 강화
✅ API 페이지네이션 구현
✅ 커스텀 매니저 모델 연결
✅ Celery Beat 스케줄 설정
✅ 전체 테스트 통과 (63/63)

**결과**: 프로덕션 준비 완료 🎉

### Crypto 기능 추가 (2025-11-27)
✅ Coin 모델 및 CoinCandle 모델 생성
✅ CoinCollectionConfig 수집 설정 관리
✅ Upbit API 통합 (pyupbit 0.2.31)
✅ Celery 태스크 추가 (코인 마스터, 캔들 수집)
✅ Django Admin 인터페이스 (재수집 액션)
✅ 테스트 커버리지 100% (38 tests)

**실제 데이터**: BTC 229개 코인 수집 완료

### OAuth 2.0 인증 도입 (2025-12-04)
✅ OAuth 2.0 Token Endpoint 구현
✅ Password Grant 및 Refresh Token Grant 지원
✅ RefreshToken 모델 생성 (Device Tracking)
✅ Token Revocation 및 Logout 기능
✅ OIDC UserInfo Endpoint 구현
✅ Keycloak 마이그레이션 준비

**현재 상태**: main 브랜치에 통합 완료

---

## 배포 가이드

### Docker Compose 배포

#### 1. 환경 설정
```bash
cp .env.example .env
nano .env  # 환경 변수 수정
```

필수 환경 변수:
```bash
# Django
DJANGO_ENV=production
DJANGO_SECRET_KEY=your-secure-secret-key
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=yourdomain.com

# Database
POSTGRES_DB=assetdb
POSTGRES_USER=asset_user
POSTGRES_PASSWORD=secure-password

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# Redis
REDIS_URL=redis://redis:6379/2

# Sentry
SENTRY_DSN=https://your-dsn@sentry.io/project-id
```

#### 2. 컨테이너 실행
```bash
docker-compose up -d --build
docker-compose logs -f
```

#### 3. 초기 설정
```bash
# 마이그레이션
docker-compose exec web python manage.py migrate

# 정적 파일 수집
docker-compose exec web python manage.py collectstatic --noinput

# 슈퍼유저 생성
docker-compose exec web python manage.py createsuperuser

# 주식 데이터 초기 동기화 (선택)
docker-compose exec web python manage.py sync_korea_stocks
```

#### 4. 서비스 확인
- Django Admin: http://yourdomain.com/admin/
- FastAPI Docs: http://yourdomain.com:8001/api/docs
- Flower (Celery): http://yourdomain.com:5555

### 로컬 개발
```bash
# Django
python manage.py runserver

# FastAPI (별도 터미널)
uvicorn main:app --reload --port 8001

# Celery Worker
celery -A config worker -l info

# Celery Beat
celery -A config beat -l info
```

### Celery Beat 스케줄

| 시간 | 태스크 | 설명 |
|-----|--------|------|
| 07:00 | sync_stock_master_task | KRX 종목 마스터 동기화 |
| 07:10 | sync_coin_master_task | Upbit 코인 마스터 동기화 |
| 07:15 | collect_crypto_candles_task | 암호화폐 캔들 데이터 수집 |
| 07:20 | sync_daily_prices_task | KRX 일별 주가 수집 |
| 07:30 | create_daily_reports_for_all_users | 리포트 생성 |
| 08:00 | send_daily_reports_via_kakao | 알림톡 발송 |

### 트러블슈팅

#### 데이터베이스 연결 실패
```bash
docker-compose ps
docker-compose logs db
docker-compose restart db web
```

#### Celery 작업 실행 안 됨
```bash
docker-compose logs celery-worker
docker-compose logs celery-beat
docker-compose exec redis redis-cli ping
docker-compose restart celery-worker celery-beat
```

#### API 응답 느림
- Redis 캐시 확인: `docker-compose exec redis redis-cli INFO keyspace`
- 로그 확인: `docker-compose logs -f api`
- 데이터베이스 쿼리 최적화 (select_related, prefetch_related)

---

## 성능 최적화

### 데이터베이스
- ✅ 인덱스 추가 (검색, 필터링 필드)
- ✅ 복합 인덱스 활용 (stock_id + trade_date)
- ✅ select_related() / prefetch_related() 사용
- ✅ 커넥션 풀 (CONN_MAX_AGE 설정)

### 캐싱 전략
- Redis DB 2 사용
- 주식 데이터: 15분 TTL
- 관심목록: 5분 TTL
- 리포트: 1시간 TTL

### Rate Limiting
- 분당 100 요청 (일반)
- 분당 5 요청 (회원가입)
- 분당 10 요청 (로그인)
- Redis DB 3 사용

---

## 보안 체크리스트

- [x] SECRET_KEY 변경
- [x] DEBUG = False (운영 환경)
- [x] ALLOWED_HOSTS 설정
- [x] HTTPS 강제 (SECURE_SSL_REDIRECT)
- [x] HSTS 설정 (1년)
- [x] CSRF 보호 활성화
- [x] JWT 토큰 기반 인증
- [x] Rate Limiting 활성화
- [x] Sentry PII 필터링
- [x] 정기적인 보안 스캔 (safety, bandit)

---

## 참고 자료

### 내부 문서
- `/docs/backup/ARCHITECTURE.md`: 시스템 아키텍처 상세
- `/docs/backup/DEPLOYMENT.md`: 배포 가이드 상세
- `/docs/backup/crypto_implementation.md`: 암호화폐 기능 구현 문서
- `/docs/backup/phase4_implementation_summary.txt`: Phase 4 작업 로그

### 외부 문서
- [Django 공식 문서](https://docs.djangoproject.com/)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Celery 공식 문서](https://docs.celeryq.dev/)
- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
- [Upbit API 문서](https://docs.upbit.com/)
- [pykrx 문서](https://github.com/sharebook-kr/pykrx)

---

## 연락처

**프로젝트 관리**: [Your Team Name]
**버그 리포트**: GitHub Issues
**문의**: [Your Email]

---

**최종 업데이트**: 2025-12-09
**문서 버전**: 1.0.0
