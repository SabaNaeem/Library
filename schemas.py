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
        from_attributes = True

class Author(BaseModel):
    first_name: str
    last_name: str
    dob: date
    gender: str
    country: str
    email: str

    class Config:
        from_attributes = True


class Category(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class User(BaseModel):
    username: str
    email: str
    password: str
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class Chats(BaseModel):
    sent: str
    session_id: str

    class Config:
        from_attributes = True

class Session(BaseModel):
    name: str
    # user_id: str

    class Config:
        from_attributes = True
