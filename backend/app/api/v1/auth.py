"""Admin authentication endpoints."""

from fastapi import APIRouter, Depends, status
from app.config import get_settings
from app.core.exceptions import UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password
from app.database.repositories.users import UserRepository
from app.dependencies import get_current_admin, get_current_user, get_user_repo
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    user_repo: UserRepository = Depends(get_user_repo),
) -> TokenResponse:
    """Authenticates an administrator and returns a signed JWT access token."""
    input_email = login_data.email.lower().strip()
    admin_env_email = settings.ADMIN_EMAIL.lower().strip()

    # Check if credentials match environment settings
    if input_email == admin_env_email and login_data.password == settings.ADMIN_PASSWORD:
        user = await user_repo.get_by_email(admin_env_email)
        if not user:
            seeded_admin = User(
                email=admin_env_email,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                role="admin",
                is_active=True,
            )
            user = await user_repo.create(seeded_admin)
        else:
            if not verify_password(login_data.password, user.password_hash):
                await user_repo.update_password(user.id, hash_password(settings.ADMIN_PASSWORD))
    else:
        user = await user_repo.get_by_email(input_email)
        if not user or not user.is_active or not verify_password(login_data.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

    # Update last login timestamp
    if user.id:
        await user_repo.update_last_login(user.id)

    access_token = create_access_token(subject=str(user.id), role=user.role)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=30,
        user_id=str(user.id),
        email=user.email,
        role=user.role,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Returns the profile of the currently authenticated administrator."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Client logout instruction (token discarded client-side)."""
    return {"message": "Successfully logged out"}
