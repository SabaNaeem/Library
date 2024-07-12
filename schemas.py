from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class EmailSchema(BaseModel):
    email: str

class Book(BaseModel):
    title: str
    summary: Optional[str] = None
    author_id: str
    categories: List[str] = []

    class Config:
        orm_mode = True

class Author(BaseModel):
    first_name: str
    last_name: str
    dob: date
    gender: str
    country: str
    email: str

    class Config:
        orm_mode = True


class Category(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class User(BaseModel):
    username: str
    email: str
    password: str
    role: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
