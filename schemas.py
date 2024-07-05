from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class BookBase(BaseModel):
    title: str
    summary: Optional[str] = None
    author_id: str

class BookCreate(BookBase):
    categories: List[str] = []


class Book(BookBase):
    id: str

    class Config:
        orm_mode = True

class AuthorBase(BaseModel):
    first_name: str
    last_name: str
    dob: date
    gender: str
    country: str
    email: str


class AuthorCreate(AuthorBase):
    pass


class Author(AuthorBase):
    id: str
    books: List[BookBase] = [{}]

    class Config:
        orm_mode = True

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: str
    books: List[BookBase] = [{}]

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    role: str

class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
