from fastapi import APIRouter, Depends, HTTPException, status
from django.contrib.auth import authenticate
from asgiref.sync import sync_to_async
from datetime import timedelta

from api.schemas import Token, UserLogin, UserCreate, UserResponse
from api.dependencies import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from apps.accounts.models import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    """
    새 사용자 등록
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

    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(user_in: UserLogin):
    """
    로그인 및 JWT 토큰 발급
    """
    user = await sync_to_async(authenticate)(
        username=user_in.username, password=user_in.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id, "username": user.username},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token)
