from fastapi import APIRouter, Depends, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.init_db import get_db
from app.limiter import limiter
from app.models import User
from app.schemas import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserOut, status_code=201)
@limiter.limit("5/second")
def create_user(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    user = User(
        username=payload.username.strip(),
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValidationError("Пользователь с таким username уже существует")
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserOut)
@limiter.limit("30/second")
def get_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("Пользователь не найден")
    return user
