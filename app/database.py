from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_async_engine(DATABASE_URL)
# Создаётся объект "движок" (engine), который управляет подключениями к базе данных

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# создаётся "фабрика сессий" (объект для создания сессий) — это объект,
# который будет создавать асинхронные сессии для работы с базой данных.
# expire_on_commit=False - чтобы сессии не истекали при коммите и транзакция не заканчивалась

class Base(DeclarativeBase):
    pass
