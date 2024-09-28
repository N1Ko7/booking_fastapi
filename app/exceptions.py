from fastapi import HTTPException, status


class BookingException(HTTPException):
    status_code = 500
    detail = "Ошибка на стороне сервера"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"


class IncorrectEmailOrPasswordException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверная почта или пароль"


class TokenExpiredException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен истек"


class NoTokenException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен отсутствует"


class IncorrectTokenFormatException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный формат токена"


class UserIsNotPresentException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED


class RoomeCannotBeBookedException(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Не осталось свободных номеров"


class BookingNotFromThisUserException(BookingException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Вы не тот пользователь, кто забронировал этот номер"


class NoSuchBookingException(BookingException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Такой брони не существует"


class NoSuchHotelException(BookingException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Такого отеля не существует"


class DateToLessThanDateFromException(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Дата окончания бронирования должна быть больше, чем дата его начала"


class NoSuchRoomException(BookingException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Такой комнаты не существует"
