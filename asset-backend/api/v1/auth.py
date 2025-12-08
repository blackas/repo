"""
OAuth 2.0 인증 엔드포인트
Keycloak 마이그레이션을 고려한 표준 준수 구현
"""
from fastapi import APIRouter, Depends, HTTPException, status
from asgiref.sync import sync_to_async
import logging

from api.schemas import (
    TokenRequest,
    TokenResponse,
    TokenRevokeRequest,
    UserInfoResponse,
    UserCreate,
    UserResponse,
    # Legacy schemas
    Token,
    UserLogin,
)
from api.dependencies import get_current_user
from apps.accounts.models import User
from apps.accounts.services import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


# ============================================================================
# OAuth 2.0 Endpoints
# ============================================================================


@router.post("/token", response_model=TokenResponse)
async def token(request: TokenRequest):
    """
    OAuth 2.0 Token Endpoint (RFC 6749)

    지원하는 grant_type:
    - password: 사용자명/비밀번호로 로그인
    - refresh_token: Refresh Token으로 Access Token 갱신

    이 엔드포인트는 OAuth 2.0 표준을 따르므로,
    향후 Keycloak으로 쉽게 마이그레이션 가능합니다.
    """
    if request.grant_type == "password":
        # Password Grant - 사용자명과 비밀번호로 인증
        if not request.username or not request.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="username and password required for password grant",
            )

        # 사용자 인증
        user = await sync_to_async(AuthService.authenticate_user)(
            request.username, request.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Access Token 생성
        access_token, expires_in = await sync_to_async(
            AuthService.create_access_token
        )(user)

        # Refresh Token 생성
        refresh_token, refresh_expires_in = await sync_to_async(
            AuthService.create_refresh_token
        )(user, request.device_type, request.device_id)

        logger.info(f"User logged in: {user.username}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=expires_in,
            refresh_expires_in=refresh_expires_in,
        )

    elif request.grant_type == "refresh_token":
        # Refresh Token Grant - Refresh Token으로 새 Access Token 발급
        if not request.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="refresh_token required for refresh_token grant",
            )

        # Refresh Token 검증
        user = await sync_to_async(AuthService.verify_refresh_token)(
            request.refresh_token
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 새 Access Token 생성
        access_token, expires_in = await sync_to_async(
            AuthService.create_access_token
        )(user)

        # Refresh Token의 남은 유효 시간 계산
        remaining_time = await sync_to_async(
            AuthService.get_token_remaining_time
        )(request.refresh_token)

        logger.debug(f"Token refreshed for user: {user.username}")

        # 기존 Refresh Token 재사용 (Rotation 정책은 향후 고려)
        return TokenResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,
            token_type="Bearer",
            expires_in=expires_in,
            refresh_expires_in=remaining_time or 0,
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported grant_type: {request.grant_type}",
        )


@router.post("/revoke", status_code=status.HTTP_200_OK)
async def revoke(request: TokenRevokeRequest):
    """
    Token Revocation Endpoint (RFC 7009)

    Refresh Token을 무효화합니다.
    """
    success = await sync_to_async(AuthService.revoke_token)(request.token)

    if success:
        logger.info("Token revoked successfully")
        return {"message": "Token revoked successfully"}
    else:
        # RFC 7009: 토큰이 없어도 200 OK 반환
        logger.warning("Token not found or already revoked")
        return {"message": "Token not found or already revoked"}


@router.get("/userinfo", response_model=UserInfoResponse)
async def userinfo(current_user: User = Depends(get_current_user)):
    """
    OIDC UserInfo Endpoint

    현재 인증된 사용자의 정보를 반환합니다.
    """
    return UserInfoResponse(
        sub=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        phone_number=current_user.phone_number,
        email_verified=bool(current_user.email),  # 향후 이메일 인증 기능 추가 시 개선
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: User = Depends(get_current_user)):
    """
    로그아웃

    현재 사용자의 모든 Refresh Token을 무효화합니다.
    """
    count = await sync_to_async(AuthService.revoke_all_user_tokens)(current_user)
    logger.info(f"User logged out: {current_user.username}, revoked {count} tokens")
    return {"message": f"Logged out successfully. {count} tokens revoked."}


# ============================================================================
# User Management Endpoints
# ============================================================================


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    """
    새 사용자 등록

    회원가입 후 /auth/token 엔드포인트로 로그인하세요.
    """
    # 사용자명 중복 체크
    username_exists = await sync_to_async(
        User.objects.filter(username=user_in.username).exists
    )()
    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # 이메일 중복 체크
    if user_in.email:
        email_exists = await sync_to_async(
            User.objects.filter(email=user_in.email).exists
        )()
        if email_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

    # 사용자 생성
    user = await sync_to_async(User.objects.create_user)(
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        phone_number=user_in.phone_number,
        receive_daily_report=user_in.receive_daily_report,
    )

    logger.info(f"New user registered: {user.username}")
    return UserResponse.model_validate(user)


# ============================================================================
# Legacy Endpoints (for backward compatibility)
# ============================================================================


@router.post("/login", response_model=Token, deprecated=True)
async def login_legacy(user_in: UserLogin):
    """
    레거시 로그인 엔드포인트 (deprecated)

    ⚠️ 이 엔드포인트는 곧 제거됩니다.
    대신 /auth/token 엔드포인트를 사용하세요.
    """
    # /auth/token 엔드포인트를 사용하도록 리다이렉트
    token_request = TokenRequest(
        grant_type="password",
        username=user_in.username,
        password=user_in.password,
        device_type="web",
    )

    response = await token(token_request)

    # Legacy 형식으로 변환
    return Token(access_token=response.access_token, token_type="bearer")
