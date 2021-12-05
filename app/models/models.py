from datetime import datetime
from typing import Optional, List

from pydantic import EmailStr
from pydantic.main import BaseModel


class Internship(BaseModel):
    name: str
    description: Optional[str] = None
    updated_at: datetime
    is_open: bool


class Application(BaseModel):
    username: Optional[str]
    internship: str
    status: str
    updated_at: datetime


class Statistic(BaseModel):
    count: int
    applications: List[Application]


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(UserBase):
    hashed_password: str
