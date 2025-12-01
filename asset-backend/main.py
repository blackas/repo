"""
FastAPI 메인 애플리케이션

Django와 통합된 FastAPI 애플리케이션입니다.
uvicorn을 사용하여 실행합니다:

    uvicorn main:app --reload --port 8001

또는 production:

    uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
"""
import os
import sys
from pathlib import Path

# Django 프로젝트 경로 추가
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Django 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import logging

from api.v1.router import api_router
from api.rate_limit import limiter

# Sentry 초기화 (FastAPI용)
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=os.getenv("DJANGO_ENV", "development"),
        integrations=[
            FastApiIntegration(),
            StarletteIntegration(),
        ],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
    )

logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="KStock Reporter API",
    description="한국 주식 리포트 시스템 REST API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Rate Limiter 등록
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 운영 환경에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sentry ASGI 미들웨어
if SENTRY_DSN:
    app.add_middleware(SentryAsgiMiddleware)


# 예외 처리
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    HTTP 예외 처리
    """
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    요청 검증 오류 처리
    """
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    일반 예외 처리
    """
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)

    # Sentry로 에러 전송
    if SENTRY_DSN:
        sentry_sdk.capture_exception(exc)

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# 라우터 등록
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """
    API 루트 엔드포인트
    """
    return {
        "message": "KStock Reporter API",
        "version": "1.0.0",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health_check():
    """
    헬스 체크 엔드포인트
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
