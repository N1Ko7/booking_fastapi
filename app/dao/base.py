from sqlalchemy import func, insert, select
from sqlalchemy.exc import SQLAlchemyError

from app.database import async_session_maker
from app.logging.logger import logger
from app.exceptions import BookingException


class BaseDAO():
    model = None

    @classmethod
    async def find_by_id(cls, model_id: int):
        try:
            async with async_session_maker() as session:
                query = select(cls.model).filter_by(id=model_id)
                result = await session.execute(query)
                return result.scalar_one_or_none()
        except (SQLAlchemyError, Exception) as error:
            logger.error(f"Some error accured in BaseDAO.find_by_id: {error}")
            raise BookingException

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        try:
            async with async_session_maker() as session:
                query = select(cls.model).filter_by(**filter_by)
                result = await session.execute(query)
                return result.scalar_one_or_none()
        except (SQLAlchemyError, Exception) as error:
            logger.error(f"Some error accured in BaseDAO.find_one_or_none: {error}")
            raise BookingException

    @classmethod
    async def find_all(cls, **filter_by):
        try:
            async with async_session_maker() as session:
                query = select(cls.model.__table__.columns).filter_by(**filter_by)
                result = await session.execute(query)
                return result.mappings().all()
        except (SQLAlchemyError, Exception) as error:
            logger.error(f"Some error accured in BaseDAO.find_all: {error}")
            raise BookingException

    @classmethod
    async def add(cls, **data):
        try:
            async with async_session_maker() as session:
                last_id_query = select(func.max(cls.model.id))
                result = await session.execute(last_id_query)
                last_id = result.scalar() or 0

                data["id"] = last_id + 1

                query = insert(cls.model).values(**data)
                await session.execute(query)
                await session.commit()
        except (SQLAlchemyError, Exception) as error:
            logger.error(f"Some error accured in BaseDAO.add: {error}")
            raise BookingException
