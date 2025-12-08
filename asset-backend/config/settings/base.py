import os
from pathlib import Path

from dotenv import load_dotenv
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change-me-in-production")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.common",
    "apps.accounts",
    "apps.stocks",
    "apps.crypto",
    "apps.reports",
    "apps.notifications",
]

AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "asset"),
        "USER": os.getenv("POSTGRES_USER", "asset_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "password"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Celery Configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

CELERY_BEAT_SCHEDULE = {
    # Stock data synchronization tasks
    "sync-stock-master-daily": {
        "task": "apps.stocks.tasks.sync_stock_master_task",
        "schedule": crontab(hour=7, minute=0),
        "options": {"expires": 3600},
    },
    # Crypto data synchronization tasks
    "sync-coin-master-daily": {
        "task": "apps.crypto.tasks.sync_coin_master_task",
        "schedule": crontab(hour=7, minute=10),
        "options": {"expires": 3600},
    },
    "collect-crypto-candles-daily": {
        "task": "apps.crypto.tasks.collect_crypto_candles_task",
        "schedule": crontab(hour=7, minute=15),
        "options": {"expires": 3600},
    },
    "sync-daily-prices-daily": {
        "task": "apps.stocks.tasks.sync_daily_prices_task",
        "schedule": crontab(hour=7, minute=20),
        "options": {"expires": 3600},
    },
    # Report generation and notification tasks
    "create_daily_reports_at_0730": {
        "task": "apps.reports.tasks.create_daily_reports_for_all_users",
        "schedule": crontab(hour=7, minute=30),
    },
    "send_daily_reports_at_0800": {
        "task": "apps.notifications.tasks.send_daily_reports_via_kakao",
        "schedule": crontab(hour=8, minute=0),
    },
}

# Kakao API Configuration
KAKAO_API_HOST = os.getenv("KAKAO_API_HOST", "")
KAKAO_API_KEY = os.getenv("KAKAO_API_KEY", "")
KAKAO_SENDER_KEY = os.getenv("KAKAO_SENDER_KEY", "")

# Cache Configuration
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/2"),
        "OPTIONS": {
            "db": "2",
            "parser_class": "redis.connection.PythonParser",
            "pool_class": "redis.BlockingConnectionPool",
            "pool_class_kwargs": {
                "max_connections": 50,
                "timeout": 20,
            },
        },
        "KEY_PREFIX": "asset",
        "TIMEOUT": 900,  # 15분 기본 타임아웃
    }
}

# Sentry Configuration
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    from config.sentry import init_sentry
    init_sentry()

# Logging
from config.logging import LOGGING  # noqa: E402, F401
