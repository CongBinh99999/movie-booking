"""Auth Router - API endpoints cho authentication.

TODO: Triển khai các endpoints sau:

=== CÓ SẴN SERVICE - Triển khai ngay ===
[ ] POST /register          - Đăng ký (service.register)
[ ] POST /login             - Đăng nhập (service.login)
[ ] POST /logout            - Đăng xuất (service.logout)
[ ] POST /refresh           - Làm mới token (service.refresh_token)
[ ] GET  /me                - Lấy thông tin user (dependency CurrentUser)
[ ] POST /me/change-password - Đổi mật khẩu (service.change_password)

=== CẦN THÊM SERVICE - Triển khai sau ===
[ ] PUT  /me                - Cập nhật profile (cần service.update_profile)
[ ] POST /forgot-password   - Gửi email reset (cần email service)
[ ] POST /reset-password    - Reset password (cần token + email service)
[ ] GET  /users             - Admin: list users (cần service.list_users)
[ ] PUT  /users/{id}/status - Admin: enable/disable (cần service.update_status)
"""

from fastapi import APIRouter, Depends
from uuid import UUID
from fastapi.security import OAuth2PasswordRequestForm

from app.modules.auth.schemas.api import (
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    ChangePasswordRequest,
    UserResponse,
    LogoutRequest
)
from app.modules.auth.dependencies import CurrentUser
from app.modules.auth.schemas.domain import UserCreate
from app.modules.auth.service import AuthServiceDep

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    response_model=UserResponse,
    summary="Đăng ký tài khoản"
)
async def register(
    data: RegisterRequest,
    auth_service: AuthServiceDep
) -> UserResponse:

    user_create = UserCreate(
        email=data.email,
        full_name=data.full_name,
        password=data.password,
        username=data.username
    )
    user = await auth_service.register(user_data=user_create)

    return UserResponse.model_validate(user)


@router.post(
        "/login", 
        response_model=TokenResponse, 
        summary="Đăng Nhập")
async def login(
    auth_service: AuthServiceDep,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> TokenResponse:
    access_token, refresh_token, access_expires_at = await auth_service.login(
        username=form_data.username,
        password=form_data.password
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=access_expires_at
    )


@router.post(
    "/logout", 
    summary="Đăng xuất"
)
async def logout(
    current_user: CurrentUser,
    data: LogoutRequest, 
    auth_service: AuthServiceDep
) -> dict[str, str]:
    await auth_service.logout(
        access_token=data.access_token, 
        refresh_token=data.refresh_token
    ) 
    return {
        "message": "Đăng xuất thành công"
    }


@router.post(
    "/refresh",
    response_model=TokenResponse, 
    summary="Tạo token mới"
)
async def refresh(
    data: RefreshTokenRequest, 
    auth_service: AuthServiceDep
) -> TokenResponse: 
    access_token, refresh_token, access_expires_at = await auth_service.refresh_token(refresh_token=data.refresh_token)
    
    return TokenResponse(
        access_token=access_token, 
        refresh_token=refresh_token, 
        expires_at=access_expires_at
    )


@router.get(
    "/me", 
    response_model=UserResponse, 
    summary="Lấy thông tin người dùng"
)
async def get_my_profile(
    current_user: CurrentUser
) -> UserResponse: 
    
    return UserResponse.model_validate(current_user)
    

@router.post(
    "/me/change-password", 
    summary="Thay đổi mật khẩu"
)
async def change_password(
    current_user: CurrentUser,
    data: ChangePasswordRequest, 
    auth_service: AuthServiceDep
) -> dict[str, str]:

    await auth_service.change_password(user_id=current_user.id, old_password=data.old_password, new_password=data.new_password)

    return {
        "message": "Thay đổi mật khẩu thành công"
    } 
    
