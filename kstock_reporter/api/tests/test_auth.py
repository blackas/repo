"""
인증 API 테스트

회원가입, 로그인 등 인증 관련 엔드포인트를 테스트합니다.
"""
import pytest
from httpx import AsyncClient

from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_register_success(async_client: AsyncClient):
    """성공적인 회원가입 테스트"""
    from asgiref.sync import sync_to_async

    user_data = {
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "securepass123",
        "phone_number": "010-9999-8888",
        "receive_daily_report": True
    }

    response = await async_client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["phone_number"] == user_data["phone_number"]
    assert "password" not in data  # 비밀번호는 응답에 포함되지 않아야 함

    # DB에 사용자가 생성되었는지 확인
    user = await sync_to_async(User.objects.get)(username="newuser")
    assert user.email == user_data["email"]
    assert await sync_to_async(user.check_password)(user_data["password"])


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_register_duplicate_username(async_client: AsyncClient, api_user):
    """중복된 사용자명으로 회원가입 시도 테스트"""
    user_data = {
        "username": api_user.username,  # 이미 존재하는 사용자명
        "email": "different@test.com",
        "password": "securepass123",
        "phone_number": "010-9999-8888",
        "receive_daily_report": True
    }

    response = await async_client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_register_duplicate_email(async_client: AsyncClient, api_user):
    """중복된 이메일로 회원가입 시도 테스트"""
    user_data = {
        "username": "differentuser",
        "email": api_user.email,  # 이미 존재하는 이메일
        "password": "securepass123",
        "phone_number": "010-9999-8888",
        "receive_daily_report": True
    }

    response = await async_client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_register_invalid_password(async_client: AsyncClient):
    """비밀번호가 너무 짧은 경우 테스트"""
    user_data = {
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "short",  # 8자 미만
        "phone_number": "010-9999-8888",
        "receive_daily_report": True
    }

    response = await async_client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_login_success(async_client: AsyncClient, api_user):
    """성공적인 로그인 테스트"""
    login_data = {
        "username": api_user.username,
        "password": "testpass123"
    }

    response = await async_client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_login_invalid_username(async_client: AsyncClient):
    """존재하지 않는 사용자명으로 로그인 시도 테스트"""
    login_data = {
        "username": "nonexistent",
        "password": "anypassword"
    }

    response = await async_client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_login_invalid_password(async_client: AsyncClient, api_user):
    """잘못된 비밀번호로 로그인 시도 테스트"""
    login_data = {
        "username": api_user.username,
        "password": "wrongpassword"
    }

    response = await async_client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_login_inactive_user(async_client: AsyncClient, api_user):
    """비활성화된 사용자로 로그인 시도 테스트"""
    from asgiref.sync import sync_to_async

    # 사용자 비활성화
    api_user.is_active = False
    await sync_to_async(api_user.save)()

    login_data = {
        "username": api_user.username,
        "password": "testpass123"
    }

    response = await async_client.post("/api/v1/auth/login", json=login_data)

    # Django's authenticate() returns None for inactive users by default
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_authenticated_request(authenticated_client: AsyncClient):
    """인증된 요청 테스트"""
    response = await authenticated_client.get("/api/v1/users/me")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "apiuser"


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_unauthenticated_request(async_client: AsyncClient):
    """인증되지 않은 요청 테스트"""
    response = await async_client.get("/api/v1/users/me")

    assert response.status_code == 401
