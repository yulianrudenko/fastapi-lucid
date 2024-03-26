import json
import aioredis

from fastapi import (
    APIRouter,
    Depends,
    Body,
    Path,
    status,
)
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..auth import get_current_user
from ..config import settings

router = APIRouter(prefix="/posts", tags=["posts"])


def get_cache() -> aioredis.Redis:
    """
    Dependency for connection to Redis cache service
    """
    redis = aioredis.from_url(settings.CACHE_URL)
    return redis


@router.post('/', status_code=status.HTTP_201_CREATED)
def add_post(
    post_data: schemas.PostCreate = Body(),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> schemas.PostOut:
    """
    Add post
    """
    post_data = {**post_data.model_dump(), 'user': current_user}
    post_obj = models.Post(**post_data)
    db.add(post_obj)
    db.commit()
    db.refresh(post_obj)
    return post_obj


@router.get('/', status_code=status.HTTP_200_OK)
async def get_posts(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
    cache: aioredis.Redis = Depends(get_cache)
) -> list[schemas.PostOut]:
    """
    Get all user posts
    """
    cached_posts: bytes | None = await cache.get(f"user{current_user.id}_posts")
    if cached_posts is not None:
        # Get data from cache
        posts_data = json.loads(cached_posts.decode("utf-8"))
        return posts_data

    # Fetch data from DB and then cache it
    posts = db.query(models.Post).filter(models.Post.user_id == current_user.id).all()
    posts_data = [schemas.PostOut(**post.__dict__ ).model_dump() for post in posts]
    await cache.set(f"user{current_user.id}_posts", json.dumps(posts_data), ex=5*60)
    return posts_data


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int = Path(title='Post ID', description='ID of the post to delete'),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete post
    """
    db.query(models.Post). \
        filter(models.Post.id == id, models.Post.user_id == current_user.id).delete()
    db.commit()
