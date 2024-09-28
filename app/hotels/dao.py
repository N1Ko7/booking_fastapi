from datetime import date

from sqlalchemy import select, and_, func

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms


class HotelsDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_all(cls, location: str, date_from: date, date_to: date):
        try:
            async with async_session_maker() as session:
                # Подсчёт свободных номеров по отелям
                free_rooms_subquery = (
                    select(
                        Rooms.hotel_id,
                        (
                                func.sum(Rooms.quantity)
                                - func.coalesce(func.count(Bookings.id), 0)
                        ).label("rooms_left"),
                    )
                    .outerjoin(
                        Bookings,
                        and_(
                            Rooms.id == Bookings.room_id,
                            Bookings.date_from <= date_to,
                            Bookings.date_to >= date_from,
                        ),
                    )
                    .group_by(Rooms.hotel_id)
                    .subquery()
                )

                # Основной запрос для получения отелей с учётом свободных номеров
                query = (
                    select(
                        cls.model.id,
                        cls.model.name,
                        cls.model.location,
                        cls.model.services,
                        cls.model.rooms_quantity,
                        cls.model.image_id,
                        free_rooms_subquery.c.rooms_left,
                    )
                    .join(
                        free_rooms_subquery, cls.model.id == free_rooms_subquery.c.hotel_id
                    )
                    .filter(
                        cls.model.location == location, free_rooms_subquery.c.rooms_left > 0
                    )
                )

                result = await session.execute(query)
                return result.mappings().all()
        except (SQLAlchemyError, Exception) as error:
            logger.error(f"Some error accured in HotelsDAO.find_all: {error}")
            raise BookingException