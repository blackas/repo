from .base import *  # noqa: F403, F401

DEBUG = True

SECRET_KEY = "test-secret-key-for-testing-only"

# 테스트용 인메모리 데이터베이스 사용
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": False,
        "OPTIONS": {
            "timeout": 20,
            "check_same_thread": False,  # Allow database access from multiple threads
        }
    }
}

# 빠른 테스트를 위한 패스워드 해시 알고리즘
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# 이메일 백엔드
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Celery 비활성화 (테스트에서는 동기 실행)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 로깅 최소화
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "ERROR",
    },
}
