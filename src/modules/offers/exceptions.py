from src.core.exceptions import BadRequestError, ForbiddenError


class NotOfferOwnerError(ForbiddenError):
    def __init__(self):
        super().__init__(detail='You are not the owner of this offer')


class OfferNotEditableError(BadRequestError):
    def __init__(self):
        super().__init__(detail='Offer cannot be edited in current status')


class OfferNotCancellableError(BadRequestError):
    def __init__(self):
        super().__init__(detail='Offer cannot be cancelled in current status')
