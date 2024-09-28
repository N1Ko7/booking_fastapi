from fastapi import HTTPException, status

UserAlreadyExistException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Пользователь уже существует",
)

IncorrectEmailOrPassword = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверная почта или пароль",
)

TokenExpireException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Токен истек",
)

TokenAbsentException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Токен отсутствует",
)

IncorrectTokenFormatException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверный формат токена",
)

UserIsNotPresentException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

RoomCannotBeBooked = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Не осталось свободных мест"
)

FetchingBookingsError = HTTPException(status_code=500, detail="Произошла ошибка при получении бронирований.")


NoSuchHotelException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Такого отеля не существует",
)

NoSuchBookingException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Такого бронирования не существует",
)

DateToLessThanDateFromException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Дата окончания бронирования не может быть раньше даты начала",
)

RoomCannotBeBookedException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Номер не может быть забронирован",
)
