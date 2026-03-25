class DomainError(Exception):
    def __init__(self, detail: str = ''):
        self.detail = detail
        super().__init__(detail)


class NotFoundError(DomainError):
    def __init__(self, detail: str = 'Not found'):
        super().__init__(detail)


class BadRequestError(DomainError):
    def __init__(self, detail: str = 'Bad request'):
        super().__init__(detail)


class UnauthorizedError(DomainError):
    def __init__(self, detail: str = 'Unauthorized'):
        super().__init__(detail)


class ForbiddenError(DomainError):
    def __init__(self, detail: str = 'Forbidden'):
        super().__init__(detail)


class ConflictError(DomainError):
    def __init__(self, detail: str = 'Conflict'):
        super().__init__(detail)


# --- Auth ---

class EmailAlreadyExistsError(ConflictError):
    def __init__(self):
        super().__init__('User with this email already exists')


class PhoneAlreadyExistsError(ConflictError):
    def __init__(self):
        super().__init__('User with this phone number already exists')


class InvalidCredentialsError(UnauthorizedError):
    def __init__(self):
        super().__init__('Invalid email/phone or password')


class AccountBlockedError(UnauthorizedError):
    def __init__(self):
        super().__init__('Account is temporarily blocked')


class AccountDeletedError(UnauthorizedError):
    def __init__(self):
        super().__init__('Account has been deleted')


class AccountNotVerifiedError(UnauthorizedError):
    def __init__(self):
        super().__init__('Email not verified. Please check your inbox.')


class InvalidVerificationCodeError(BadRequestError):
    def __init__(self):
        super().__init__('Invalid or expired verification code')


# --- Offers ---

class NotOfferOwnerError(ForbiddenError):
    def __init__(self):
        super().__init__('You are not the owner of this offer')


class OfferNotEditableError(BadRequestError):
    def __init__(self):
        super().__init__('Offer cannot be edited in current status')


class OfferNotCancellableError(BadRequestError):
    def __init__(self):
        super().__init__('Offer cannot be cancelled in current status')


# --- Reservations ---

class OfferNotAvailableError(BadRequestError):
    def __init__(self):
        super().__init__('Offer is not available for reservation')


class NotFarmerError(ForbiddenError):
    def __init__(self):
        super().__init__('Only farmers can create reservations')


class NotReservationParticipantError(ForbiddenError):
    def __init__(self):
        super().__init__('You are not a participant of this reservation')


class ReservationNotCancellableError(BadRequestError):
    def __init__(self):
        super().__init__('Reservation cannot be cancelled in current status')


class ReservationNotCompletableError(BadRequestError):
    def __init__(self):
        super().__init__('Reservation cannot be completed in current status')


# --- Reviews ---

class ReservationNotCompletedError(BadRequestError):
    def __init__(self):
        super().__init__('Can only review completed reservations')


class AlreadyReviewedError(BadRequestError):
    def __init__(self):
        super().__init__('You have already reviewed this reservation')


class CannotReviewSelfError(BadRequestError):
    def __init__(self):
        super().__init__('Cannot review yourself')
