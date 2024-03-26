from fastapi import (
    APIRouter,
    Depends,
    Body,
    Path,
    status,
)
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session

from .. import models, schemas
from ..db import get_db
from ..auth import get_current_user


router = APIRouter(prefix="/posts", tags=["posts"])


@router.post('/', status_code=status.HTTP_201_CREATED)
def add_post(
    post_data: schemas.PostCreate = Body(),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> schemas.PostOut:
    """
    Add post
    """
    post_data = {**post_data.dict(), 'user': current_user}
    post_obj = models.Post(**post_data)
    db.add(post_obj)
    db.commit()
    db.refresh(post_obj)
    return post_obj


@router.get('/', status_code=status.HTTP_200_OK)
@cache(expire=5*60)
def get_posts(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list[schemas.PostOut]:
    """
    Get all user posts
    """
    posts = db.query(models.Post).filter(models.Post.user_id == current_user.id).all()
    return posts


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
