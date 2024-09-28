import asyncio
from datetime import date

from fastapi import APIRouter
from pydantic import parse_obj_as

from app.bookings.dao import BookingsDAO
from app.exceptions import DateToLessThanDateFromException, NoSuchHotelException
from app.hotels.dao import HotelsDAO
from app.hotels.rooms.dao import RoomsDAO
from app.hotels.schemas import SHotelWithRoomsLeft, SHotel

from fastapi_cache.decorator import cache

hotels_router = APIRouter(
    prefix="/hotels",
    tags=["Отели"],
)


@hotels_router.get("/{location}")
@cache(expire=60)
async def get_hotels(
    location: str, date_from: date, date_to: date
): #-> list[SHotelWithRoomsLeft]
    if date_to < date_from:
        raise DateToLessThanDateFromException
    hotels = await HotelsDAO.find_all(
        location=location, date_from=date_from, date_to=date_to
    )
    hotels_json = parse_obj_as(list[SHotel], hotels)
    return hotels_json


@hotels_router.get("/id/{hotel_id}")
async def get_hotel_by_id(hotel_id: int) -> SHotel:
    hotel = await HotelsDAO.find_one_or_none(id=hotel_id)

    if not hotel:
        raise NoSuchHotelException

    return hotel
