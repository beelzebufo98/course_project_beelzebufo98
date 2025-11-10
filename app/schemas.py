from decimal import Decimal, InvalidOperation
from typing import Optional

from pydantic import BaseModel, Field, validator


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)


class UserOut(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class CategoryOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class WishBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    link: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=2000)
    category_id: Optional[int] = Field(default=None)
    is_fulfilled: bool = Field(default=False)


class WishCreate(WishBase):
    price_estimate: float = Field(ge=0)

    @validator("price_estimate", pre=True)
    def normalize_price(cls, v):
        return Decimal(v).quantize(Decimal("0.01"))


class WishUpdate(WishBase):
    price_estimate: Optional[str] = None

    @validator("price_estimate", pre=True)
    def normalize_price(cls, v):
        if v is None or v == "":
            return None
        try:
            return str(Decimal(v).quantize(Decimal("0.01")))
        except (InvalidOperation, ValueError):
            raise ValueError("price_estimate must be a valid number ≥ 0")


class WishOut(BaseModel):
    id: int
    title: str
    link: Optional[str]
    price_estimate: float
    notes: Optional[str]
    is_fulfilled: bool
    category: Optional[CategoryOut]
    owner_id: int

    class Config:
        from_attributes = True
