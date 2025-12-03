"""
Django ORM을 FastAPI와 통합하기 위한 설정
"""
import os
import django
from django.conf import settings

# Django 설정 초기화
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


def get_db():
    """
    Django ORM 사용을 위한 의존성
    FastAPI에서는 실제 DB 세션이 필요 없지만,
    일관성을 위해 제공
    """
    try:
        yield
    finally:
        pass
