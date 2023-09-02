from fastapi import HTTPException, status


class BookingException(HTTPException):
    status_code = 500
    detail = ''

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(BookingException):
    status_code = status.HTTP_409_CONFLICT,
    detail = 'User is already exists'


class IncorrectEmailOrPasswordException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED,
    detail = 'Incorrect Email Or Password'


class TokenExpiredException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED,
    detail = 'Token time has passed'


class TokenAbsentException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Token missing'


class IncorrectFormatTokenException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED,
    detail = 'Incorrect format token'


class UserIsNotPresentException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED


class RoomCannotBeBooked(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'No available rooms'


class DateFromCannotBeAfterDateTo(BookingException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Check-in date cannot be later than check-out date'


class CannotBookHotelForLongPeriod(BookingException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'It is not possible to book a hotel for more than a month'


class CannotAddDataToDatabase(BookingException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = 'Cannot add new record'