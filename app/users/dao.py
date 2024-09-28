from sqlalchemy import update

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.users.models import Users


class UsersDAO(BaseDAO):
    model = Users

    @classmethod
    async def update_refresh_token(cls, user_id: int, refresh_token: str):
        async with async_session_maker() as session:
            query = (
                update(cls.model)
                .where(cls.model.id == user_id)
                .values(refresh_token=refresh_token)
            )
            await session.execute(query)
            await session.commit()
