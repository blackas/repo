# Django + FastAPI 하이브리드 아키텍처 분석

## 개요

이 프로젝트는 **Django**와 **FastAPI**를 결합한 하이브리드 아키텍처를 사용합니다. Django는 백엔드 인프라와 관리자 기능을, FastAPI는 고성능 REST API를 제공합니다.

## 아키텍처 구조

```
┌─────────────────────────────────────────────────────────────┐
│                        클라이언트                              │
└─────────────────────────────────────────────────────────────┘
                │                           │
                │ REST API                  │ Admin UI
                │ (JSON)                    │ (HTML)
                ▼                           ▼
┌──────────────────────┐       ┌──────────────────────┐
│   FastAPI Server     │       │   Django Server      │
│   (포트 8001)         │       │   (포트 8000)         │
│                      │       │                      │
│ - REST API 엔드포인트 │       │ - Django Admin       │
│ - Pydantic 스키마    │       │ - 관리자 페이지       │
│ - JWT 인증           │       │                      │
└──────────────────────┘       └──────────────────────┘
                │                           │
                └───────────┬───────────────┘
                            ▼
                ┌──────────────────────┐
                │   Django ORM         │
                │   (공유 계층)         │
                │                      │
                │ - 모델 정의          │
                │ - DB 마이그레이션    │
                │ - 비즈니스 로직      │
                └──────────────────────┘
                            │
                            ▼
                ┌──────────────────────┐
                │   PostgreSQL DB      │
                └──────────────────────┘
```

## 통합 방식

### 1. Django 초기화 (main.py)

FastAPI 앱이 시작될 때 Django를 먼저 초기화합니다:

```python
# main.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()  # Django ORM 초기화

from fastapi import FastAPI
app = FastAPI()
```

**핵심 포인트:**
- `django.setup()`을 호출하여 Django ORM, 설정, 모델을 초기화
- FastAPI가 Django의 모델을 직접 사용할 수 있게 됨

### 2. Django ORM 사용 (api/v1/stocks.py)

FastAPI 엔드포인트에서 Django 모델을 직접 사용:

```python
from asgiref.sync import sync_to_async
from apps.stocks.models import Stock, DailyPrice

@router.get("/stocks/")
async def list_stocks():
    @sync_to_async
    def get_stocks():
        return list(Stock.objects.filter(is_active=True))

    stocks = await get_stocks()
    return stocks
```

**핵심 포인트:**
- Django ORM은 동기(sync) 방식 → FastAPI는 비동기(async) 방식
- `asgiref.sync.sync_to_async`로 Django ORM 호출을 비동기로 래핑

### 3. 스키마 변환 (Pydantic)

Django 모델 → Pydantic 스키마 변환:

```python
from pydantic import BaseModel, ConfigDict

class StockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    market: Optional[str]

# 사용
stock = await sync_to_async(Stock.objects.get)(code="005930")
return StockResponse.model_validate(stock)
```

## 역할 분담

### Django의 역할

| 기능 | 설명 | 위치 |
|------|------|------|
| **ORM & 모델** | 데이터베이스 스키마 정의 | `apps/*/models.py` |
| **마이그레이션** | DB 스키마 변경 관리 | `apps/*/migrations/` |
| **Admin 페이지** | 관리자 UI 제공 | `http://localhost:8000/admin/` |
| **비즈니스 로직** | 도메인 로직, 서비스 계층 | `apps/*/services.py` |
| **Celery 작업** | 백그라운드 작업, 스케줄링 | `apps/*/tasks.py` |
| **미들웨어** | 로깅, 예외 처리 | `apps/common/middleware.py` |
| **설정 관리** | 환경별 설정 (dev/prod) | `config/settings/` |

### FastAPI의 역할

| 기능 | 설명 | 위치 |
|------|------|------|
| **REST API** | JSON 기반 HTTP API | `api/v1/*.py` |
| **API 문서** | Swagger UI, ReDoc 자동 생성 | `http://localhost:8001/api/docs` |
| **스키마 검증** | Pydantic을 통한 요청/응답 검증 | `api/schemas/*.py` |
| **JWT 인증** | 토큰 기반 인증 | `api/dependencies.py` |
| **Rate Limiting** | API 속도 제한 | `api/rate_limit.py` |
| **비동기 처리** | async/await 기반 고성능 API | 모든 엔드포인트 |

## 데이터 흐름 예시

### 예시 1: 주식 목록 조회 API

```
1. [클라이언트] GET /api/v1/stocks/
   ↓
2. [FastAPI] stocks.py의 list_stocks() 실행
   ↓
3. [sync_to_async] Django ORM 호출 래핑
   ↓
4. [Django ORM] Stock.objects.filter(is_active=True) 쿼리
   ↓
5. [PostgreSQL] SELECT * FROM stocks_stock WHERE is_active = true
   ↓
6. [Django Model] Stock 객체 리스트 반환
   ↓
7. [Pydantic] StockResponse 스키마로 변환
   ↓
8. [FastAPI] JSON 응답 반환
```

### 예시 2: 주식 데이터 동기화 (Celery)

```
1. [Celery Beat] 매일 07:00 스케줄 트리거
   ↓
2. [Celery Worker] apps/stocks/tasks.py 실행
   ↓
3. [Django Service] apps/stocks/services.py 호출
   ↓
4. [pykrx] 한국거래소 API 호출
   ↓
5. [Django ORM] Stock.objects.bulk_create() 대량 저장
   ↓
6. [PostgreSQL] 데이터 저장
```

## 장점 (Pros)

### 1. 🚀 **최고의 성능과 개발자 경험**

- **FastAPI의 고성능:** 비동기 I/O로 동시 요청 처리 능력 우수
- **자동 API 문서:** Swagger UI로 즉시 테스트 가능
- **타입 안정성:** Pydantic으로 런타임 데이터 검증

### 2. 🛠️ **강력한 인프라 (Django)**

- **검증된 ORM:** 복잡한 쿼리, 트랜잭션, 마이그레이션 관리
- **Admin 페이지:** 코드 없이 데이터 관리 UI 제공
- **생태계:** 인증, 권한, 캐싱 등 풍부한 라이브러리

### 3. 🔄 **역할 분리**

```
Django  → "무거운 작업" (ORM, Admin, Celery, 비즈니스 로직)
FastAPI → "빠른 API" (REST 엔드포인트, 실시간 응답)
```

- 각 프레임워크가 자신이 가장 잘하는 일을 담당
- 관심사의 분리로 유지보수성 향상

### 4. 📦 **점진적 마이그레이션 가능**

- 기존 Django 프로젝트에 FastAPI를 점진적으로 추가 가능
- 레거시 API를 유지하면서 새 API는 FastAPI로 개발

### 5. 🔐 **통합된 인증**

- Django User 모델을 FastAPI에서 그대로 사용
- JWT 토큰 생성/검증을 공유
- OAuth 2.0 표준 준수로 Keycloak 등으로 마이그레이션 용이

### 6. 📊 **관리 편의성**

- **Django Admin:** 데이터 확인, 수정, 관리
- **Flower:** Celery 작업 모니터링
- **Swagger UI:** API 테스트 및 문서화

## 단점 (Cons)

### 1. 🏗️ **복잡도 증가**

- 두 프레임워크를 이해하고 관리해야 함
- 초기 학습 곡선이 높음
- 설정 파일, 의존성이 많아짐

### 2. 🔄 **sync_to_async 오버헤드**

```python
# 비동기 래핑 필요
stocks = await sync_to_async(Stock.objects.all)()
```

- Django ORM 호출마다 비동기 래핑 필요
- 성능 오버헤드 발생 가능
- 코드 가독성 저하

### 3. 🚀 **배포 복잡도**

- 두 개의 서버 프로세스 실행 필요:
  - Django (Gunicorn): 포트 8000
  - FastAPI (Uvicorn): 포트 8001
- Nginx 리버스 프록시 설정 복잡
- 컨테이너화 시 리소스 사용량 증가

### 4. 🐛 **디버깅 어려움**

- 에러가 Django와 FastAPI 사이에서 발생할 수 있음
- 스택 트레이스가 복잡해짐
- 동기/비동기 혼용으로 데드락 가능성

### 5. 🔌 **Django의 일부 기능 사용 불가**

- Django의 미들웨어를 FastAPI에서 직접 사용 불가
- Django Form, Template 등은 사용 안 함
- 두 프레임워크 간 일부 기능 중복 구현 필요

### 6. 💾 **트랜잭션 관리 주의 필요**

```python
# Django의 @transaction.atomic을 async 함수에서 사용 불가
# 별도 처리 필요
@sync_to_async
@transaction.atomic
def create_stock_with_prices(data):
    # ...
```

## 대안 아키텍처와의 비교

### 1. Django + Django REST Framework (DRF)

```
장점: 단일 프레임워크, 간단한 구조
단점: DRF은 동기식, 성능이 FastAPI보다 낮음
```

### 2. FastAPI + SQLAlchemy

```
장점: 순수 비동기, 높은 성능
단점: Django Admin 없음, 생태계가 Django보다 작음
```

### 3. FastAPI + Django (현재 아키텍처)

```
장점: 두 프레임워크의 장점 결합
단점: 복잡도 증가, 배포/운영 오버헤드
```

## 이 아키텍처를 사용해야 하는 경우

### ✅ 추천하는 경우

1. **관리자 페이지가 필요한 경우**
   - Django Admin으로 빠르게 데이터 관리 UI 구축

2. **복잡한 비즈니스 로직이 있는 경우**
   - Django ORM의 강력한 쿼리 기능 활용
   - Celery로 백그라운드 작업 처리

3. **고성능 API가 필요한 경우**
   - 대량의 동시 요청 처리
   - 비동기 I/O로 응답 속도 향상

4. **점진적 현대화**
   - 기존 Django 프로젝트에 FastAPI를 점진적으로 도입

### ❌ 추천하지 않는 경우

1. **단순한 CRUD API만 필요한 경우**
   - DRF만으로 충분

2. **팀원이 비동기 프로그래밍에 익숙하지 않은 경우**
   - 학습 곡선이 가파름

3. **마이크로서비스 아키텍처**
   - 각 서비스를 독립적으로 FastAPI 또는 Django로 구축하는 것이 나음

4. **극도로 높은 성능이 필요한 경우**
   - Go, Rust 등 네이티브 언어 고려

## 운영 시 고려사항

### 1. 모니터링

```
- Django: Django Debug Toolbar, django-extensions
- FastAPI: Prometheus + Grafana
- 통합: Sentry (에러 추적)
```

### 2. 로깅

```python
# 공통 로깅 설정 (config/logging.py)
LOGGING = {
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
        }
    }
}
```

### 3. 배포 전략

```yaml
# docker-compose.yml
services:
  web:      # Django (Admin, Celery Beat)
    command: gunicorn config.wsgi:application
  api:      # FastAPI (REST API)
    command: uvicorn main:app
  worker:   # Celery Worker
    command: celery -A config worker
```

## 결론

이 하이브리드 아키텍처는 **Django의 안정성과 생태계**, **FastAPI의 성능과 개발자 경험**을 모두 활용하는 강력한 접근 방식입니다.

**적합한 프로젝트:**
- 복잡한 도메인 로직 + 고성능 API가 필요한 경우
- 관리자 기능 + 모바일/웹 클라이언트를 모두 지원해야 하는 경우
- 기존 Django 프로젝트의 API 성능 개선이 필요한 경우

**주의사항:**
- 초기 학습 비용과 복잡도 증가를 감수할 수 있어야 함
- 팀원들이 비동기 프로그래밍에 익숙해야 함
- 운영 인프라가 두 서버를 관리할 수 있어야 함

## 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Django 공식 문서](https://docs.djangoproject.com/)
- [asgiref 문서](https://github.com/django/asgiref)
- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
