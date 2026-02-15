from src.core.exceptions import ConflictError, UnauthorizedError


class EmailAlreadyExistsError(ConflictError):
    def __init__(self):
        super().__init__(detail='User with this email already exists')


class PhoneAlreadyExistsError(ConflictError):
    def __init__(self):
        super().__init__(detail='User with this phone number already exists')


class InvalidCredentialsError(UnauthorizedError):
    def __init__(self):
        super().__init__(detail='Invalid email/phone or password')


class AccountBlockedError(UnauthorizedError):
    def __init__(self):
        super().__init__(detail='Account is temporarily blocked')


class AccountDeletedError(UnauthorizedError):
    def __init__(self):
        super().__init__(detail='Account has been deleted')
