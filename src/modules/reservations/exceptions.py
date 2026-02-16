from src.core.exceptions import BadRequestError, ForbiddenError


class OfferNotAvailableError(BadRequestError):
    def __init__(self):
        super().__init__(detail='Offer is not available for reservation')


class NotFarmerError(ForbiddenError):
    def __init__(self):
        super().__init__(detail='Only farmers can create reservations')


class NotReservationParticipantError(ForbiddenError):
    def __init__(self):
        super().__init__(detail='You are not a participant of this reservation')


class ReservationNotCancellableError(BadRequestError):
    def __init__(self):
        super().__init__(detail='Reservation cannot be cancelled in current status')


class ReservationNotCompletableError(BadRequestError):
    def __init__(self):
        super().__init__(detail='Reservation cannot be completed in current status')
