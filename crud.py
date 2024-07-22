import models
import schemas
from fastapi import HTTPException
from sqlalchemy.orm import Session


def create_author(db: Session, author: schemas.Author):
    db_author = models.Author(**author.dict())
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author

def is_verified(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user and not db_user.is_verified:
        db_user.is_verified = True
        db.commit()
        db.refresh(db_user)  # Refresh the instance to reflect the updated values
        return db_user
    return None


def get_authors(db: Session, skip: int = 0, limit: int = 10):
    authors = db.query(models.Author).filter(models.Author.active == True).offset(skip).limit(limit).all()
    result = []
    for author in authors:
        books = db.query(models.Book).join(models.Author).filter(models.Book.author_id == author.id).all()
        result.append({
            "first_name": author.first_name,
            "last_name": author.last_name,
            "dob": author.dob,
            "gender": author.gender,
            "country": author.country,
            "email": author.email,
            "books": books
        })
    return result


def get_author(db: Session, author_id: str):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()
    result = []
    books = db.query(models.Book).join(models.Author).filter(models.Book.author_id == author_id).all()
    result.append({
        "first_name": author.first_name,
        "last_name": author.last_name,
        "dob": author.dob,
        "gender": author.gender,
        "country": author.country,
        "email": author.email,
        "books": books
    })
    return result


def update_author(db: Session, author_id: str, author: schemas.Author):
    db_author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if db_author:
        if not db_author.active:
            raise HTTPException(status_code=400, detail="Author is not active")
        for key, value in author.dict().items():
            setattr(db_author, key, value)
        db.commit()
        db.refresh(db_author)
    return db_author


def delete_author(db: Session, author_id: str):
    db_author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if db_author and db_author.active:
        setattr(db_author, "active", False)
        db.commit()
    return db_author


def create_category(db: Session, category: schemas.Category):
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_category(db: Session, category_id: str):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    result = []
    books = db.query(models.Book).join(models.book_categories).filter(
        models.book_categories.category_id == category_id).all()
    result.append({
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "books": books
    })
    return result


def get_categories(db: Session, skip: int = 0, limit: int = 10):
    categories = db.query(models.Category).filter(models.Category.active == True).offset(skip).limit(limit).all()
    result = []
    for category in categories:
        books = db.query(models.Book).join(models.book_categories).filter(
            models.book_categories.category_id == category.id).all()
        result.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "books": books
        })
    return result


def update_category(db: Session, category_id: str, category: schemas.Category):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        if not db_category.active:
            raise HTTPException(status_code=400, detail="Category is not active")
        for key, value in category.dict().items():
            setattr(db_category, key, value)
        db.commit()
        db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: str):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category and db_category.active:
        setattr(db_category, "active", False)
        db.commit()
    return db_category


def create_book(db: Session, book: schemas.Book):
    # Check if author exists
    author = db.query(models.Author).filter(models.Author.id == book.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    # Check if categories exist
    categories = []
    for category_id in book.categories:
        category = db.query(models.Category).filter(models.Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail=f"Category with ID {category_id} not found")
        categories.append(category)

    # Create book
    db_book = models.Book(
        title=book.title,
        summary=book.summary,
        author_id=book.author_id
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    # Add categories to book
    for category in categories:
        db_book_category = models.book_categories(book_id=db_book.id, category_id=category.id)
        db.add(db_book_category)
    db.commit()

    # Refresh book to include categories
    db.refresh(db_book)

    return db_book


def get_books(db: Session, skip: int = 0, limit: int = 10):
    books = db.query(models.Book).filter(models.Book.active == True).offset(skip).limit(limit).all()
    result = []
    for book in books:
        categories = db.query(models.Category).join(models.book_categories).filter(
            models.book_categories.book_id == book.id).all()
        result.append({
            "id": book.id,
            "title": book.title,
            "summary": book.summary,
            "categories": categories
        })
    return result


def get_book(db: Session, book_id: str):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    result = []
    categories = db.query(models.Category).join(models.book_categories).filter(
        models.book_categories.book_id == book.id).all()
    result.append({
        "id": book.id,
        "title": book.title,
        "summary": book.summary,
        "categories": categories
    })
    return result


def update_book(db: Session, book_id: str, book: schemas.Book):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book:
        if not db_book.active:
            raise HTTPException(status_code=400, detail="Book is not active")
        for key, value in book.dict().items():
            setattr(db_book, key, value)
        db.commit()
        db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: str):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book and db_book.active:
        setattr(db_book, "active", False)
        db.commit()
    return db_book

def create_session(db: Session, session: schemas.Session, current_user: models.User):
    session_dict = session.dict()
    session_dict["user_id"] = current_user.id
    db_session = models.Sessions(**session_dict)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return session

def get_session(db: Session, name: str):
    session = db.query(models.Sessions).filter(models.Sessions.name == name).first()
    return session

def get_user_session(db: Session, skip: int = 0, limit: int = 10):
    sessions = db.query(models.Sessions).filter().offset(skip).limit(limit).all()
    result = []
    for session in sessions:
        result.append({
            "id": session.id,
            "name": session.name,
            "created_at": session.created_at,
            "modified_at": session.modified_at
        })
    return result

def get_chat(db: Session, session_id: str):
    chats = db.query(models.Chats).filter(models.Chats.session_id == session_id).all()
    result = []
    for chat in chats:
        result.append({
            "sent": chat.sent,
            "receive": chat.receive
        })
    return result