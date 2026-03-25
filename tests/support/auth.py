from src.domain.services.auth_service import AuthService
from src.domain.models.user import User


def make_auth_header(user: User) -> dict:
    token = AuthService._create_token(str(user.id), user.role.value)
    return {'Authorization': f'Bearer {token}'}
