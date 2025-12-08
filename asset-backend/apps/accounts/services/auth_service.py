"""
인증 관련 비즈니스 로직
OAuth 2.0 표준을 따르는 토큰 관리 서비스
"""
from datetime import timedelta, datetime, timezone
from typing import Optional, Tuple
from django.contrib.auth import authenticate
from django.conf import settings
from jose import jwt, JWTError
import secrets
import logging

from apps.accounts.models import User, RefreshToken

logger = logging.getLogger(__name__)

# JWT 설정 - settings에서 가져오거나 기본값 사용
SECRET_KEY = getattr(settings, "JWT_SECRET_KEY", settings.SECRET_KEY)
ALGORITHM = "HS256"

# 토큰 유효기간 - 환경변수로 설정 가능
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60)  # 1시간
REFRESH_TOKEN_EXPIRE_DAYS = getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7)  # 7일


class AuthService:
    """인증 관련 비즈니스 로직"""

    @staticmethod
    def create_access_token(user: User) -> Tuple[str, int]:
        """
        Access Token 생성

        Args:
            user: 사용자 객체

        Returns:
            (token, expires_in): JWT 토큰과 만료 시간(초)
        """
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.now(timezone.utc) + expires_delta

        to_encode = {
            "user_id": user.id,
            "username": user.username,
            "exp": expire,
            "type": "access",  # 토큰 타입 명시
        }

        try:
            token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            logger.debug(f"Access token created for user {user.username}")
            return token, int(expires_delta.total_seconds())
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise

    @staticmethod
    def create_refresh_token(
        user: User, device_type: Optional[str] = None, device_id: Optional[str] = None
    ) -> Tuple[str, int]:
        """
        Refresh Token 생성 및 DB 저장

        Args:
            user: 사용자 객체
            device_type: 디바이스 타입 (web, ios, android)
            device_id: 디바이스 고유 ID

        Returns:
            (token, expires_in): JWT 토큰과 만료 시간(초)
        """
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        expire = datetime.now(timezone.utc) + expires_delta

        # 고유한 jti (JWT ID) 생성 - 보안을 위해 DB에는 jti만 저장
        jti = secrets.token_urlsafe(32)

        to_encode = {
            "user_id": user.id,
            "jti": jti,
            "exp": expire,
            "type": "refresh",  # 토큰 타입 명시
        }

        try:
            token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

            # DB에 jti만 저장 (전체 토큰 저장 시 보안 위험)
            RefreshToken.objects.create(
                user=user,
                token=jti,
                expires_at=expire,
                device_type=device_type,
                device_id=device_id,
            )

            logger.debug(
                f"Refresh token created for user {user.username}, device: {device_type}"
            )
            return token, int(expires_delta.total_seconds())
        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            raise

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        사용자 인증

        Args:
            username: 사용자명 또는 이메일
            password: 비밀번호

        Returns:
            User: 인증된 사용자 객체 또는 None
        """
        try:
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                logger.info(f"User authenticated successfully: {username}")
                return user
            logger.warning(f"Authentication failed for user: {username}")
            return None
        except Exception as e:
            logger.error(f"Authentication error for user {username}: {e}")
            return None

    @staticmethod
    def verify_refresh_token(token: str) -> Optional[User]:
        """
        Refresh Token 검증

        Args:
            token: Refresh token JWT

        Returns:
            User: 유효한 경우 사용자 객체, 그렇지 않으면 None
        """
        try:
            # JWT 디코딩
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # 토큰 타입 확인
            if payload.get("type") != "refresh":
                logger.warning("Invalid token type (expected: refresh)")
                return None

            jti = payload.get("jti")
            user_id = payload.get("user_id")

            if not jti or not user_id:
                logger.warning("Missing jti or user_id in token payload")
                return None

            # DB에서 토큰 확인
            refresh_token = RefreshToken.objects.filter(
                token=jti, user_id=user_id
            ).select_related("user").first()

            if not refresh_token:
                logger.warning(f"Refresh token not found: jti={jti}")
                return None

            if not refresh_token.is_valid():
                logger.warning(
                    f"Refresh token is not valid (revoked or expired): jti={jti}"
                )
                return None

            logger.debug(f"Refresh token verified for user: {refresh_token.user.username}")
            return refresh_token.user

        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying refresh token: {e}")
            return None

    @staticmethod
    def revoke_token(token: str) -> bool:
        """
        토큰 무효화

        Args:
            token: 무효화할 refresh token JWT

        Returns:
            bool: 무효화 성공 여부
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            jti = payload.get("jti")

            if not jti:
                logger.warning("Token revocation failed: missing jti")
                return False

            refresh_token = RefreshToken.objects.filter(token=jti).first()
            if refresh_token:
                refresh_token.revoke()
                logger.info(f"Token revoked successfully: jti={jti}")
                return True

            logger.warning(f"Token not found for revocation: jti={jti}")
            return False

        except JWTError as e:
            logger.warning(f"JWT decoding failed during revocation: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error revoking token: {e}")
            return False

    @staticmethod
    def revoke_all_user_tokens(user: User) -> int:
        """
        사용자의 모든 토큰 무효화 (로그아웃)

        Args:
            user: 사용자 객체

        Returns:
            int: 무효화된 토큰 수
        """
        try:
            count = RefreshToken.objects.filter(
                user=user, revoked_at__isnull=True
            ).update(revoked_at=datetime.now(timezone.utc))

            logger.info(f"Revoked {count} tokens for user: {user.username}")
            return count
        except Exception as e:
            logger.error(f"Error revoking all tokens for user {user.username}: {e}")
            raise

    @staticmethod
    def get_token_remaining_time(token: str) -> Optional[int]:
        """
        토큰의 남은 유효 시간 계산 (선택적 기능)

        Args:
            token: Refresh token JWT

        Returns:
            int: 남은 시간(초), 유효하지 않으면 None
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            exp = payload.get("exp")
            if exp:
                remaining = exp - datetime.now(timezone.utc).timestamp()
                return int(remaining) if remaining > 0 else 0
            return None
        except (JWTError, Exception):
            return None
