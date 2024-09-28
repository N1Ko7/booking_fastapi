from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.bookings.router import booking_router as router_bookings
from app.config import settings
from app.users.router import router as router_users
from app.hotels.router import hotels_router as router_hotels
from app.pages.router import router as router_pages
from app.images.router import router as router_images

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield


app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), "static")

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(router_users)
app.include_router(router_hotels)
app.include_router(router_bookings)
app.include_router(router_images)
app.include_router(router_pages)


origins = [
    "hhtp://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control_Allow-Headers",
                   "Access-Control_Allow-Origin", "Authorization"]
)
