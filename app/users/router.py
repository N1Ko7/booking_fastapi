from fastapi import APIRouter, Response, Depends
from jose import jwt, JWTError

from app.config import settings
from app.exceptions import UserAlreadyExistException, IncorrectEmailOrPassword, IncorrectTokenFormatException, \
    UserIsNotPresentException, TokenAbsentException
from app.users.auth import get_password_hash, aunthenticate_user, create_token
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user, get_current_admin_user
from app.users.models import Users
from app.users.schemas import SUserAuth

router = APIRouter(
    prefix="/auth",
    tags=["Auth & Пользователи"],
)

@router.post("/register")
async def register_user(user_data: SUserAuth):
    existing_user = await UsersDAO.find_one_or_none(email=user_data.email)
    if existing_user:
        raise UserAlreadyExistException
    hashed_password = get_password_hash(user_data.password)
    await UsersDAO.add(email=user_data.email, hashed_password=hashed_password)


@router.post("/login")
async def login_user(response: Response, user_data: SUserAuth):
    user = await aunthenticate_user(user_data.email, user_data.password)
    if not user:
        raise IncorrectEmailOrPassword
    access_token = create_token({"sub": str(user.id)}, minutes=settings.JWT_EXPIRE_TIME_ACCESS_TOKEN)
    refresh_token = create_token({"sub": str(user.id)}, days=settings.JWT_EXPIRE_TIME_REFRESH_TOKEN)

    await UsersDAO.update_refresh_token(user.id, refresh_token)

    response.set_cookie("booking_access_token", access_token, httponly=True)
    response.set_cookie("booking_refresh_token", refresh_token, httponly=True)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("booking_access_token")


@router.get("/me")
async def read_users_me(current_user: Users = Depends(get_current_user)):
    return current_user


@router.get("/all")
async def read_users_me(current_user: Users = Depends(get_current_admin_user)):
    return await UsersDAO.find_all()

