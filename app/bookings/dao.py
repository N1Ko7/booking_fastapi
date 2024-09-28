from datetime import date
from typing import Optional

from sqlalchemy import and_, func, insert, or_, outerjoin, select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.exceptions import BookingException, BookingNotFromThisUserException, NoSuchBookingException,\
    NoSuchRoomException
from app.hotels.rooms.models import Rooms
from app.logging.logger import logger


# DAO - Data Access Object
class BookingsDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def add(cls, user_id: int, room_id: int, date_from: date, date_to: date):
        """
        WITH booked_rooms AS (
                SELECT * FROM bookings WHERE room_id = 1 AND
            (date_from >= '2023-10-01' AND date_from <='2023-10-05') OR
            (date_from <= '2023-10-01'  AND date_to > '2023-10-01')
        )

        SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
        LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        WHERE rooms.id = 1
        GROUP BY rooms.quantity, booked_rooms.room_id
        """

        try:
            async with async_session_maker() as session:
                booked_rooms = (
                    select(Bookings)
                    .where(
                        and_(
                            Bookings.room_id == room_id,
                            or_(
                                and_(
                                    Bookings.date_from >= date_from,
                                    Bookings.date_from <= date_to,
                                ),
                                and_(
                                    Bookings.date_from <= date_from,
                                    Bookings.date_to > date_from,
                                ),
                            ),
                        )
                    )
                    .cte("booked_rooms")
                )

                get_rooms_left = (
                    select(
                        (Rooms.quantity - func.count(booked_rooms.c.room_id)).label(
                            "rooms_left"
                        )
                    )
                    .select_from(
                        outerjoin(Rooms, booked_rooms, booked_rooms.c.room_id == Rooms.id)
                    )
                    .where(Rooms.id == room_id)
                    .group_by(Rooms.quantity, booked_rooms.c.room_id)
                )

                rooms_left = await session.execute(get_rooms_left)
                rooms_left: int = rooms_left.scalar()

                if rooms_left is None:
                    return rooms_left

                if rooms_left > 0:
                    get_price = select(Rooms.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar()

                    last_id_query = select(func.max(cls.model.id))
                    result = await session.execute(last_id_query)
                    last_id = result.scalar() or 0

                    new_id = last_id + 1

                    add_booking = (
                        insert(Bookings)
                        .values(
                            id=new_id,
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        .returning(Bookings)
                    )

                    new_booking = await session.execute(add_booking)
                    await session.commit()

                    return new_booking.scalar()

                else:
                    return None
        except (SQLAlchemyError, Exception, NoSuchRoomException) as error:
            logger.error(f"Some error accured in BookingsDAO.add: {error}")
            raise BookingException

    @classmethod
    async def delete_booking(cls, user_id, booking_id):
        try:
            async with async_session_maker() as session:
                booking = await session.get(Bookings, booking_id)

                if not booking:
                    raise NoSuchBookingException

                if booking.user_id != user_id:
                    raise BookingNotFromThisUserException

                await session.delete(booking)
                await session.commit()
        except (SQLAlchemyError, Exception) as error:
            logger.error(f"Some error accured in  BookingsDAO.delete_booking: {error}")
            raise BookingException

    @classmethod
    async def find_by_id_load_room_and_hotel(cls, booking_id: int) -> Optional[Bookings]:
        try:
            async with async_session_maker() as session:
                query = (
                    session.query(Bookings)
                    .options(joinedload(Bookings.room_id).joinedload(Rooms.hotel_id))
                    .filter(Bookings.id == booking_id)
                    .first()
                )

                result = await session.execute(query)
                booking_obj = result.scalar_one_or_none()

                return booking_obj
        except (SQLAlchemyError, Exception) as error:
            logger.error(f"Some error accured in  BookingsDAO.find_by_id_load_room_and_hotel: {error}")
            raise BookingException
