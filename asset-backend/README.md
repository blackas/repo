# Asset Backend

Django 기반 자산 관리 백엔드 시스템 - 주식, 암호화폐 데이터 수집 및 리포트 생성 프로젝트입니다.

## 주요 기능

- Django 5.x 기반 백엔드 (Admin, ORM, 마이그레이션)
- FastAPI 기반 REST API (고성능, 자동 문서화)
- PostgreSQL 데이터베이스
- Celery + Redis를 통한 비동기 작업 처리
- pykrx를 이용한 한국 주식 시세 수집
- 사용자별 관심목록 기반 일일 리포트 생성
- 카카오 알림톡(비즈 메시지) 발송
- JWT 인증 시스템
- Redis 캐싱 전략

## 기술 스택

- **Backend**: Django 5.1, FastAPI 0.115, Python 3.11+
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7
- **Task Queue**: Celery 5.4
- **Authentication**: JWT (python-jose)
- **Testing**: pytest, pytest-django, factory-boy, httpx
- **Code Quality**: black, flake8, mypy

## 프로젝트 구조

```
asset-backend/
├── config/                 # Django 설정
│   ├── settings/           # 환경별 설정 분리
│   │   ├── __init__.py
│   │   ├── base.py         # 공통 설정
│   │   ├── development.py  # 개발 환경
│   │   ├── production.py   # 운영 환경
│   │   └── test.py         # 테스트 환경
│   ├── logging.py          # 로깅 설정
│   ├── celery.py
│   └── urls.py
├── api/                    # FastAPI 애플리케이션
│   ├── v1/                 # API v1
│   │   ├── auth.py         # 인증 (로그인, 회원가입)
│   │   ├── users.py        # 사용자 관리
│   │   ├── stocks.py       # 주식 데이터
│   │   ├── watchlists.py   # 관심목록
│   │   ├── reports.py      # 리포트
│   │   └── router.py       # 라우터 통합
│   ├── schemas/            # Pydantic 스키마
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── stock.py
│   │   ├── watchlist.py
│   │   └── report.py
│   ├── database.py         # Django ORM 통합
│   └── dependencies.py     # JWT 인증 의존성
├── apps/
│   ├── common/             # 공통 유틸리티
│   │   ├── models.py       # TimeStampedModel, SoftDeleteModel
│   │   ├── exceptions.py   # 커스텀 예외
│   │   ├── middleware.py   # 로깅, 예외 처리 미들웨어
│   │   ├── utils.py        # 유틸리티 함수
│   │   ├── validators.py   # 검증 함수
│   │   └── cache.py        # 캐싱 유틸리티
│   ├── accounts/           # 사용자 관리
│   │   ├── models.py       # User, WatchList, WatchListItem
│   │   ├── admin.py
│   │   └── tests/
│   ├── stocks/             # 주식 데이터
│   │   ├── models.py       # Stock, DailyPrice
│   │   ├── services.py     # KRX 데이터 수집 로직 (개선됨)
│   │   ├── admin.py
│   │   └── tests/
│   ├── reports/            # 리포트 생성
│   │   ├── models.py       # DailyReport
│   │   ├── services.py     # 리포트 생성 로직 (개선됨)
│   │   ├── tasks.py        # Celery 작업
│   │   ├── admin.py
│   │   └── tests/
│   └── notifications/      # 알림 발송
│       ├── models.py       # NotificationLog
│       ├── services/       # 카카오 API 클라이언트 (개선됨)
│       ├── tasks.py        # Celery 작업
│       ├── admin.py
│       └── tests/
├── main.py                 # FastAPI 메인 애플리케이션
├── logs/                   # 로그 파일
├── requirements.txt
├── pytest.ini
├── .flake8
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

## 시작하기

### 1. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 수정하여 필요한 값 설정
# - DJANGO_SECRET_KEY (운영 환경에서는 반드시 변경)
# - POSTGRES_* (데이터베이스 설정)
# - KAKAO_* (카카오 API 설정)
```

### 2. Docker Compose로 실행

```bash
# 컨테이너 시작 (Django + FastAPI + Celery + DB + Redis)
docker-compose up -d

# 마이그레이션 실행
docker-compose exec web python manage.py migrate

# 슈퍼유저 생성
docker-compose exec web python manage.py createsuperuser

# 주식 데이터 동기화 (선택사항)
docker-compose exec web python manage.py sync_korea_stocks

# 서비스 접속
# - Django Admin: http://localhost:8000/admin/
# - FastAPI Docs: http://localhost:8001/api/docs
# - FastAPI ReDoc: http://localhost:8001/api/redoc
```

### 3. 로컬 개발 환경

```bash
# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
export DJANGO_ENV=development

# 마이그레이션
python manage.py migrate

# Django 개발 서버 실행
python manage.py runserver

# 별도 터미널에서 FastAPI 실행
uvicorn main:app --reload --port 8001
```

## API 사용법

### FastAPI 엔드포인트

FastAPI는 자동 문서화를 제공합니다:
- Swagger UI: http://localhost:8001/api/docs
- ReDoc: http://localhost:8001/api/redoc

### 인증

```bash
# 1. 회원가입
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "phone_number": "010-1234-5678"
  }'

# 2. 로그인 (JWT 토큰 발급)
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword123"
  }'

# 응답: {"access_token": "eyJ...", "token_type": "bearer"}
```

### API 요청 예시

```bash
# 3. 인증이 필요한 API 호출
TOKEN="your-jwt-token-here"

# 현재 사용자 정보 조회
curl -X GET "http://localhost:8001/api/v1/users/me" \
  -H "Authorization: Bearer $TOKEN"

# 주식 목록 조회
curl -X GET "http://localhost:8001/api/v1/stocks/?limit=10" \
  -H "Authorization: Bearer $TOKEN"

# 특정 주식 조회
curl -X GET "http://localhost:8001/api/v1/stocks/005930" \
  -H "Authorization: Bearer $TOKEN"

# 관심목록 생성
curl -X POST "http://localhost:8001/api/v1/watchlists/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "내 포트폴리오"}'

# 관심목록에 종목 추가
curl -X POST "http://localhost:8001/api/v1/watchlists/1/items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"stock_id": 1}'

# 리포트 목록 조회
curl -X GET "http://localhost:8001/api/v1/reports/" \
  -H "Authorization: Bearer $TOKEN"
```

### 주요 API 엔드포인트

| 엔드포인트 | 메소드 | 설명 | 인증 |
|-----------|--------|------|------|
| `/api/v1/auth/register` | POST | 회원가입 | ❌ |
| `/api/v1/auth/login` | POST | 로그인 | ❌ |
| `/api/v1/users/me` | GET | 현재 사용자 정보 | ✅ |
| `/api/v1/users/me` | PUT | 사용자 정보 수정 | ✅ |
| `/api/v1/stocks/` | GET | 주식 목록 | ✅ |
| `/api/v1/stocks/{code}` | GET | 주식 상세 | ✅ |
| `/api/v1/stocks/{code}/prices` | GET | 주식 가격 데이터 | ✅ |
| `/api/v1/watchlists/` | GET | 관심목록 조회 | ✅ |
| `/api/v1/watchlists/` | POST | 관심목록 생성 | ✅ |
| `/api/v1/watchlists/{id}/items` | POST | 종목 추가 | ✅ |
| `/api/v1/reports/` | GET | 리포트 목록 | ✅ |
| `/api/v1/reports/{id}` | GET | 리포트 상세 | ✅ |

## 테스트

```bash
# 모든 테스트 실행
pytest

# 커버리지 리포트 생성
pytest --cov=apps --cov-report=html

# 특정 앱만 테스트
pytest apps/stocks/tests/

# 특정 테스트만 실행
pytest apps/stocks/tests/test_services.py::TestSyncStockMasterFromKrx
```

## 코드 품질

```bash
# Black으로 코드 포매팅
black .

# Flake8으로 린팅
flake8 .

# Mypy로 타입 체크
mypy apps/
```

## 관리자 기능

Admin 페이지(`/admin/`)에서 다음 기능을 사용할 수 있습니다:

- 사용자 및 관심목록 관리
- 주식 및 가격 데이터 조회
- 리포트 생성 내역 확인
- 알림 발송 로그 조회

## Celery 작업 스케줄

기본 스케줄 (config/settings/base.py):
- 07:30 - 일일 리포트 생성 (`create_daily_reports_for_all_users`)
- 08:00 - 카카오 알림톡 발송 (`send_daily_reports_via_kakao`)

## 로깅

로그 파일은 `logs/` 디렉토리에 저장됩니다:
- `django.log` - 일반 애플리케이션 로그
- `error.log` - 에러 로그
- `celery.log` - Celery 작업 로그
- `stocks.log` - 주식 데이터 수집 로그

## 환경 변수

주요 환경 변수는 `.env.example` 파일을 참고하세요.

- `DJANGO_ENV` - 환경 설정 (development/production/test)
- `DJANGO_SECRET_KEY` - Django 시크릿 키
- `DJANGO_DEBUG` - 디버그 모드
- `POSTGRES_*` - 데이터베이스 설정
- `CELERY_*` - Celery 설정
- `KAKAO_*` - 카카오 API 설정

## 보안 주의사항

1. 운영 환경에서는 반드시 `DJANGO_SECRET_KEY`를 변경하세요
2. `DJANGO_DEBUG=false`로 설정하세요
3. `ALLOWED_HOSTS`를 적절히 설정하세요
4. HTTPS를 사용하세요 (운영 환경)
5. 환경 변수 파일(.env)을 버전 관리에 포함하지 마세요

## 라이선스

MIT
