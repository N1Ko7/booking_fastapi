from datetime import date

from fastapi import APIRouter, Request, Depends
from pydantic import parse_obj_as

from app.bookings.dao import BookingsDAO
from app.bookings.schemas import SBooking
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.exceptions import RoomCannotBeBookedException

booking_router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@booking_router.get("")
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
        raise RoomCannotBeBookedException

    booking_dict = parse_obj_as(SBooking, booking).dict()

    return booking_dict


@booking_router.delete("/{booking_id}")
async def delete_booking(booking_id: int, user: Users = Depends(get_current_user)):
    await BookingsDAO.delete_booking(user.id, booking_id)


@booking_router.get("/{booking_id}")
async def get_booking_by_id(booking_id: int, user: Users = Depends(get_current_user)):
    booking = await BookingsDAO.find_one_or_none(id=booking_id)

    if not booking:
        raise NoSuchBookingException

    return booking
