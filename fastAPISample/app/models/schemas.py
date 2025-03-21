from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str  # Pydantic v2에서는 EmailStr 사용 시 email_validator 패키지 필요
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class User(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}  # orm_mode 대신 from_attributes 사용

class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}  # orm_mode 대신 from_attributes 사용