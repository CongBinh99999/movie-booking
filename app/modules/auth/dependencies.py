from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.modules.auth.schemas.domain import UserDTO
from app.modules.auth.exceptions import InsufficientPermissionsError
from app.modules.auth.service import AuthServiceDep

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthServiceDep
) -> UserDTO:
    return await auth_service.get_authenticated_user(token)


CurrentUser = Annotated[UserDTO, Depends(get_current_user)]


def require_role(required_role: str):
    """Factory function tạo dependency kiểm tra role.

    Args:
        required_role: Role yêu cầu (vd: "admin", "staff").

    Returns:
        Dependency function kiểm tra role của user.
    """
    async def role_checker(current_user: CurrentUser) -> UserDTO:
        if current_user.role != required_role:
            raise InsufficientPermissionsError(required_role=required_role)
        return current_user

    return role_checker


RequireAdmin = Depends(require_role("admin"))
