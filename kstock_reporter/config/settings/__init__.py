import os

# 환경 변수로 설정 파일 선택
env = os.getenv("DJANGO_ENV", "development")

if env == "production":
    from .production import *  # noqa
elif env == "test":
    from .test import *  # noqa
else:
    from .development import *  # noqa
