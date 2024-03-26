from fastapi import FastAPI

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from .config import settings
from .routers import users, posts


app = FastAPI()
redis = aioredis.from_url(settings.CACHE_URL)
FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

app.include_router(users.router, tags=["users"])
app.include_router(posts.router, tags=["posts"])
