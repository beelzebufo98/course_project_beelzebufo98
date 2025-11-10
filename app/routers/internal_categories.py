from fastapi import APIRouter, Depends, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.init_db import get_db
from app.limiter import limiter
from app.models import Category
from app.schemas import CategoryCreate, CategoryOut

router = APIRouter(prefix="/internal/categories", tags=["Internal: Categories"])


@router.post("", response_model=CategoryOut, status_code=201)
@limiter.limit("5/second")
def create_category(
    request: Request,
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
):
    category = Category(name=category_in.name)
    db.add(category)
    try:
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise ValidationError("Категория с таким названием уже существует")
    return category


@router.get("", response_model=list[CategoryOut])
@limiter.limit("10/second")
def list_categories(
    request: Request,
    db: Session = Depends(get_db),
):
    categories = db.query(Category).order_by(Category.name.asc()).all()
    return categories


@router.get("/{category_id}", response_model=CategoryOut)
@limiter.limit("20/second")
def get_category(
    request: Request,
    category_id: int,
    db: Session = Depends(get_db),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise NotFoundError("Категория не найдена")
    return category


@router.delete("/{category_id}", status_code=204)
@limiter.limit("5/minute")
def delete_category(
    request: Request,
    category_id: int,
    db: Session = Depends(get_db),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise NotFoundError("Категория не найдена")

    db.delete(category)
    db.commit()
    return None
