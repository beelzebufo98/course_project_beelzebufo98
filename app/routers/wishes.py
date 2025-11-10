from fastapi import APIRouter, Depends, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.init_db import get_db
from app.limiter import limiter
from app.models import Wish
from app.schemas import WishCreate, WishOut, WishUpdate

router = APIRouter(prefix="/wishes", tags=["Wishes"])


@router.post("", response_model=WishOut, status_code=201)
@limiter.limit("10/second")
def create_wish(
    request: Request,
    wish_in: WishCreate,
    db: Session = Depends(get_db),
):
    wish = Wish(**wish_in.model_dump())

    db.add(wish)
    try:
        db.commit()
        db.refresh(wish)
    except IntegrityError as e:
        db.rollback()
        raise ValidationError(f"Ошибка при создании пожелания: {e}")
    return wish


@router.get("/{wish_id}", response_model=WishOut)
@limiter.limit("30/second")
def get_wish(
    request: Request,
    wish_id: int,
    db: Session = Depends(get_db),
):
    wish = db.query(Wish).filter(Wish.id == wish_id).first()
    if not wish:
        raise NotFoundError("Пожелание не найдено")

    return wish


@router.patch("/{wish_id}", response_model=WishOut)
@limiter.limit("30/minute")
def update_wish(
    request: Request,
    wish_id: int,
    wish_in: WishUpdate,
    db: Session = Depends(get_db),
):
    wish = db.query(Wish).filter(Wish.id == wish_id).first()
    if not wish:
        raise NotFoundError("Пожелание не найдено")

    for key, value in wish_in.model_dump(exclude_unset=True).items():
        setattr(wish, key, value)

    db.add(wish)
    try:
        db.commit()
        db.refresh(wish)
    except IntegrityError:
        db.rollback()
        raise ValidationError("Ошибка при обновлении пожелания")

    return wish


@router.delete("/{wish_id}", status_code=204)
@limiter.limit("10/minute")
def delete_wish(
    request: Request,
    wish_id: int,
    db: Session = Depends(get_db),
):
    wish = db.query(Wish).filter(Wish.id == wish_id).first()
    if not wish:
        raise NotFoundError("Пожелание не найдено")

    db.delete(wish)
    db.commit()
    return None
