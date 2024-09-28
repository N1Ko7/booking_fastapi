from datetime import date

from fastapi import APIRouter, Depends
from pydantic import parse_obj_as

from fastapi_versioning import version
from fastapi_cache.decorator import cache

from app.bookings.dao import BookingsDAO
from app.bookings.schemas import SBooking
from app.exceptions import NoSuchBookingException, RoomeCannotBeBookedException
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users

booking_router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@booking_router.get("")
@cache(expire=30)
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBooking]:
    return await BookingsDAO.find_all(user_id=user.id)


@booking_router.post("")
async def add_booking(
    room_id: int,
    date_from: date,
    date_to: date,
    user: Users = Depends(get_current_user),
):
    booking = await BookingsDAO.add(user.id, room_id, date_from, date_to)

    if not booking:
        raise RoomeCannotBeBookedException

    booking_dict = parse_obj_as(SBooking, booking).dict()
    send_booking_confirmation_email.delay(booking_dict, user.email)

    return booking_dict


@booking_router.delete("/{booking_id}")
async def delete_booking(booking_id: int, user: Users = Depends(get_current_user)):
    await BookingsDAO.delete_booking(user.id, booking_id)


@booking_router.get("/{booking_id}")
@cache(expire=30)
async def get_booking_by_id(booking_id: int, user: Users = Depends(get_current_user)):
    booking = await BookingsDAO.find_one_or_none(id=booking_id)

    if not booking:
        raise NoSuchBookingException

    return booking
