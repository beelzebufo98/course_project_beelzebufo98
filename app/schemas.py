from decimal import Decimal, InvalidOperation
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserCreate(StrictModel):
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


class CategoryCreate(StrictModel):
    name: str = Field(min_length=1, max_length=100)


class CategoryOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class WishBase(StrictModel):
    title: str = Field(min_length=1, max_length=120)
    link: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=2000)
    category_id: Optional[int] = Field(default=None)
    is_fulfilled: bool = Field(default=False)


class WishCreate(WishBase):
    owner_id: int
    price_estimate: Decimal = Field(ge=Decimal("0"), max_digits=10, decimal_places=2)

    @field_validator("price_estimate", mode="before")
    @classmethod
    def normalize_price(cls, v):
        if v is None:
            return Decimal("0.00")
        try:
            return Decimal(v).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            raise ValueError("price_estimate must be a valid non-negative number")


class WishUpdate(WishBase):
    price_estimate: Optional[Decimal] = Field(
        default=None, ge=Decimal("0"), max_digits=10, decimal_places=2
    )

    @field_validator("price_estimate", mode="before")
    @classmethod
    def normalize_price(cls, v):
        if v in (None, ""):
            return None
        try:
            return Decimal(v).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            raise ValueError("price_estimate must be a valid non-negative number")


class WishOut(BaseModel):
    id: int
    title: str
    link: Optional[str]
    price_estimate: Decimal
    notes: Optional[str]
    is_fulfilled: bool
    category: Optional[CategoryOut]
    owner_id: int

    @field_serializer("price_estimate")
    def _ser_price(self, v: Decimal):
        return float(v.quantize(Decimal("0.01")))

    class Config:
        from_attributes = True
