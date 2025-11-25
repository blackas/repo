"""
Sentry 설정
"""
import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging


def init_sentry():
    """
    Sentry 초기화
    """
    sentry_dsn = os.getenv("SENTRY_DSN", "")
    environment = os.getenv("DJANGO_ENV", "development")

    if not sentry_dsn:
        logging.warning("SENTRY_DSN not configured. Sentry will not be initialized.")
        return

    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        # 통합
        integrations=[
            DjangoIntegration(
                transaction_style="url",
                middleware_spans=True,
                signals_spans=True,
                cache_spans=True,
            ),
            CeleryIntegration(
                monitor_beat_tasks=True,
                exclude_beat_tasks=[],
            ),
            RedisIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
            ),
        ],
        # 성능 모니터링
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        # 프로파일링
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
        # 오류 샘플링
        sample_rate=1.0,
        # PII 데이터 전송 여부
        send_default_pii=False,
        # 릴리스 버전
        release=os.getenv("RELEASE_VERSION", "unknown"),
        # 추가 컨텍스트
        before_send=before_send_handler,
    )

    logging.info(f"Sentry initialized for environment: {environment}")


def before_send_handler(event, hint):
    """
    이벤트 전송 전 처리
    민감한 정보 필터링 등
    """
    # 민감한 정보가 포함된 이벤트 필터링
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]
        # 특정 예외는 Sentry로 보내지 않음
        if exc_type.__name__ in ["KeyboardInterrupt", "SystemExit"]:
            return None

    # 개인정보 마스킹
    if "request" in event:
        if "data" in event["request"]:
            data = event["request"]["data"]
            if isinstance(data, dict):
                # 비밀번호 마스킹
                if "password" in data:
                    data["password"] = "***REDACTED***"
                # 토큰 마스킹
                if "token" in data:
                    data["token"] = "***REDACTED***"

    return event
