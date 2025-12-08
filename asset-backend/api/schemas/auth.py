from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


# ============================================================================
# OAuth 2.0 Token Schemas
# ============================================================================


class TokenRequest(BaseModel):
    """
    OAuth 2.0 Token Request
    Supports password and refresh_token grant types
    """

    grant_type: Literal["password", "refresh_token"] = Field(
        ..., description="OAuth 2.0 grant type"
    )

    # For password grant
    username: Optional[str] = Field(None, min_length=1, description="Username or email")
    password: Optional[str] = Field(None, min_length=1, description="User password")

    # For refresh_token grant
    refresh_token: Optional[str] = Field(None, description="Refresh token JWT")

    # Optional device info (for multi-platform support)
    device_type: Optional[Literal["web", "ios", "android"]] = Field(
        None, description="Device type"
    )
    device_id: Optional[str] = Field(None, description="Device unique identifier")

    @field_validator("username", "password")
    @classmethod
    def validate_password_grant(cls, v, info):
        """Validate that username and password are provided for password grant"""
        # Note: This validation happens after the model is created
        # We'll do grant_type specific validation in the endpoint
        return v


class TokenResponse(BaseModel):
    """OAuth 2.0 Token Response"""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="Bearer", description="Token type (always Bearer)")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    refresh_expires_in: int = Field(
        ..., description="Refresh token expiration time in seconds"
    )


class TokenRevokeRequest(BaseModel):
    """Token Revocation Request (RFC 7009)"""

    token: str = Field(..., description="The token to revoke")
    token_type_hint: Optional[Literal["access_token", "refresh_token"]] = Field(
        None, description="Hint about the type of token"
    )


class UserInfoResponse(BaseModel):
    """
    OIDC UserInfo Response
    Returns information about the authenticated user
    """

    sub: str = Field(..., description="Subject identifier (user ID)")
    username: str = Field(..., description="Username")
    email: Optional[str] = Field(None, description="Email address")
    phone_number: Optional[str] = Field(None, description="Phone number")
    email_verified: bool = Field(default=False, description="Whether email is verified")


# ============================================================================
# Legacy Schemas (for backward compatibility)
# ============================================================================


class Token(BaseModel):
    """Legacy token schema - deprecated, use TokenResponse instead"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""

    user_id: Optional[int] = None


class UserLogin(BaseModel):
    """Legacy login schema - deprecated, use TokenRequest instead"""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
