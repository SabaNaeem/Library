import uuid
from sqlalchemy import Column, String, Date, ForeignKey, Text, Table, TIMESTAMP, CheckConstraint, DateTime, func, \
    Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Author(Base):
    __tablename__ = 'authors'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    dob = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    country = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    books = relationship("Book", back_populates="author")
    active = Column(Boolean, nullable=False, default=True)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    books = relationship("Book", secondary='book_categories', back_populates="categories")
    created_at = Column(DateTime, server_default=func.now())
    active = Column(Boolean, nullable=False, default=True)


class Book(Base):
    __tablename__ = 'books'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    summary = Column(Text)
    author_id = Column(UUID(as_uuid=True), ForeignKey('authors.id'), nullable=False)
    author = relationship("Author", back_populates="books")
    categories = relationship("Category", secondary='book_categories', back_populates="books")
    created_at = Column(DateTime, server_default=func.now())
    active = Column(Boolean, nullable=False, default=True)


class book_categories(Base):
    __tablename__ = 'book_categories'
    book_id = Column(UUID(as_uuid=True), ForeignKey('books.id', ondelete="CASCADE"), primary_key=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id', ondelete="CASCADE"), primary_key=True)


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(String(50), CheckConstraint("role IN ('admin', 'user')"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    is_verified = Column(Boolean, nullable=False, default=False)

    sessions = relationship('Sessions', back_populates='users')

class Chats(Base):
    __tablename__ = 'chats'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    sent = Column(Text, nullable=False)
    receive = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    sessions = relationship('Sessions', back_populates='chats')

class Sessions(Base):
    __tablename__ = 'sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    users = relationship('User', back_populates='sessions')
    chats = relationship('Chats', back_populates='sessions')
