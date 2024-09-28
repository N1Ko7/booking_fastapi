from datetime import date

from sqlalchemy import select, func, and_

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.models import Rooms


class RoomsDAO(BaseDAO):
    model = Rooms

    @classmethod
    async def find_all_by_hotel_id(cls, hotel_id: int, date_from: date, date_to: date):
        async with async_session_maker() as session:
            # Запрос для поиска всех комнат по отелю
            query = (
                select(
                    cls.model.id,
                    cls.model.hotel_id,
                    cls.model.name,
                    cls.model.description,
                    cls.model.services,
                    cls.model.price,
                    cls.model.quantity,
                    cls.model.image_id,
                    (cls.model.price * func.extract("day", date_to - date_from)).label(
                        "total_cost"
                    ),
                    (
                        cls.model.quantity - func.coalesce(func.count(Bookings.id), 0)
                    ).label(
                        "rooms_left"
                    ),  # Вычисление оставшихся комнат
                )
                .outerjoin(
                    Bookings,
                    and_(
                        cls.model.id == Bookings.room_id,
                        Bookings.date_from < date_to,  # Проверка пересечения дат
                        Bookings.date_to > date_from,
                    ),
                )
                .where(cls.model.hotel_id == hotel_id)
                .group_by(cls.model.id)
            )

            result = await session.execute(query)
            rooms = result.mappings().all()

            # Проверка, есть ли комнаты для данного отеля
            if not rooms:
                return None

            return rooms
