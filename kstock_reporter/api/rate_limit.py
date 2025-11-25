"""
API Rate Limiting 설정
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request


def get_user_identifier(request: Request) -> str:
    """
    사용자 식별자 생성
    인증된 사용자는 user_id, 아니면 IP 주소 사용
    """
    # Authorization 헤더에서 사용자 정보 추출
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        # JWT 토큰이 있으면 토큰 기반 rate limiting
        token = auth_header[7:]
        return f"token:{token[:20]}"  # 토큰 앞부분만 사용

    # 인증되지 않은 사용자는 IP 기반
    return get_remote_address(request)


# Rate Limiter 인스턴스 생성
limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=["100/minute", "1000/hour"],
    storage_uri="redis://redis:6379/3",
)

# 엔드포인트별 rate limit 설정
RATE_LIMITS = {
    # 인증 엔드포인트 (더 엄격)
    "auth_register": "5/minute",
    "auth_login": "10/minute",

    # 조회 엔드포인트 (관대)
    "read": "100/minute",

    # 쓰기 엔드포인트 (중간)
    "write": "50/minute",

    # 관리자 엔드포인트 (매우 관대)
    "admin": "200/minute",
}
