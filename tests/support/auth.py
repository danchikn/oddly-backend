from src.modules.auth.service import create_access_token
from src.modules.users.models import User


def make_auth_header(user: User) -> dict:
    token = create_access_token(str(user.id), user.role.value)
    return {'Authorization': f'Bearer {token}'}
