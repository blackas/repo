"""
FastAPI 의존성 정의
OAuth 2.0 표준에 따른 토큰 검증
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from asgiref.sync import sync_to_async
from django.conf import settings
import logging

from apps.accounts.models import User

logger = logging.getLogger(__name__)

# JWT 설정 - AuthService와 동일한 설정 사용
SECRET_KEY = getattr(settings, "JWT_SECRET_KEY", settings.SECRET_KEY)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60)  # 1시간

security = HTTPBearer()


# ============================================================================
# Legacy Functions (deprecated - AuthService 사용 권장)
# ============================================================================


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    JWT 액세스 토큰 생성 (Legacy)

    ⚠️ Deprecated: apps.accounts.services.AuthService.create_access_token 사용 권장
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})  # 토큰 타입 추가
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ============================================================================
# Token Verification
# ============================================================================


def verify_token(token: str) -> dict:
    """
    JWT 토큰 검증

    Args:
        token: JWT 토큰 문자열

    Returns:
        dict: 토큰 페이로드

    Raises:
        HTTPException: 토큰이 유효하지 않은 경우
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Access Token인지 확인 (OAuth 2.0 표준)
        token_type = payload.get("type")
        if token_type and token_type != "access":
            logger.warning(f"Invalid token type: {token_type} (expected: access)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Use access token for API requests.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# User Dependencies
# ============================================================================


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    현재 인증된 사용자 가져오기

    Authorization 헤더에서 Bearer 토큰을 추출하고 검증한 후,
    해당 토큰의 사용자를 반환합니다.

    Args:
        credentials: HTTPBearer에서 자동으로 추출한 인증 정보

    Returns:
        User: 인증된 사용자 객체

    Raises:
        HTTPException: 토큰이 유효하지 않거나 사용자를 찾을 수 없는 경우
    """
    token = credentials.credentials
    payload = verify_token(token)

    user_id: int = payload.get("user_id")
    if user_id is None:
        logger.warning("Token payload missing user_id")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user = await sync_to_async(User.objects.get)(id=user_id)
    except User.DoesNotExist:
        logger.warning(f"User not found: id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    현재 사용자가 관리자인지 확인

    Args:
        current_user: get_current_user에서 가져온 현재 사용자

    Returns:
        User: 관리자 사용자 객체

    Raises:
        HTTPException: 사용자가 관리자가 아닌 경우
    """
    if not current_user.is_superuser:
        logger.warning(f"Non-superuser attempted admin access: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
