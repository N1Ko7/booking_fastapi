from datetime import datetime

from fastapi import Request, Depends, Response
from jose import jwt, JWTError

from app.config import settings
from app.exceptions import TokenExpireException, TokenAbsentException, IncorrectTokenFormatException, \
    UserIsNotPresentException
from app.users.auth import create_token
from app.users.dao import UsersDAO
from app.users.models import Users


def get_token(request: Request):
    token = request.cookies.get("booking_access_token")
    if not token:
        raise TokenAbsentException
    return token


async def get_current_user(request: Request, response: Response, token: str = Depends(get_token)):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM
        )
    except JWTError:
        refresh_token = request.cookies.get("booking_refresh_token")
        if not refresh_token:
            raise IncorrectTokenFormatException

        try:
            payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
            user_id: str = payload.get("sub")
            if not user_id:
                raise UserIsNotPresentException

            user = await UsersDAO.find_by_id(int(user_id))
            if not user or user.refresh_token != refresh_token:
                raise TokenAbsentException

            new_access_token = create_token({"sub": str(user.id)}, minutes=settings.JWT_EXPIRE_TIME_ACCESS_TOKEN)
            response.set_cookie("booking_access_token", new_access_token, httponly=True, secure=True)

            payload = jwt.decode(new_access_token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
        except JWTError:
            raise IncorrectTokenFormatException

    exprie: str = payload.get("exp")
    if (not exprie) or (int(exprie) < datetime.utcnow().timestamp()):
        raise TokenExpireException

    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException
    user = await UsersDAO.find_by_id(int(user_id))
    if not user:
        raise UserIsNotPresentException

    return user


async def get_current_admin_user(current_user: Users = Depends(get_current_user)):
    # if current_user.role != "admin":
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return current_user
