import os
import schemas
import crud
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from models import Base, User
from database import engine, session_scope
from auth import (authenticate_user, create_access_token, get_current_user, get_current_admin_user, get_password_hash,
                  get_db)
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv


Base.metadata.create_all(bind=engine)

app = FastAPI()
load_dotenv()


@app.post("/token")
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30)))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


@app.post("/signup/")
async def create_user(user: schemas.User, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, password_hash=hashed_password, email=user.email, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/")
async def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


# CRUD operations for Authors
@app.post("/authors/", dependencies=[Depends(get_current_admin_user)])
async def create_author(author: schemas.Author, db: Session = Depends(get_db)):
    return crud.create_author(db=db, author=author)


@app.get("/authors/")
async def read_authors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_authors(db=db, skip=skip, limit=limit)


@app.get("/authors/{author_id}")
async def read_author(author_id: str, db: Session = Depends(get_db)):
    db_author = crud.get_author(db=db, author_id=author_id)
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return db_author


@app.put("/authors/{author_id}", dependencies=[Depends(get_current_admin_user)])
async def update_author(author_id: str, author: schemas.Author, db: Session = Depends(get_db)):
    db_author = crud.update_author(db=db, author_id=author_id, author=author)
    if db_author is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_author


@app.delete("/authors/{author_id}", dependencies=[Depends(get_current_admin_user)])
async def delete_author(author_id: str, db: Session = Depends(get_db)):
    db_author = crud.delete_author(db=db, author_id=author_id)
    if not db_author.active:
        raise HTTPException(status_code=404, detail="Author deleted")
    return db_author


@app.post("/categories/", dependencies=[Depends(get_current_admin_user)])
def create_category(category: schemas.Category, db: Session = Depends(get_db)):
    return crud.create_category(db=db, category=category)


@app.get("/categories/")
def read_categories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_categories(db=db, skip=skip, limit=limit)


@app.get("/categories/{category_id}")
def read_category(category_id: str, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


@app.put("/categories/{category_id}", dependencies=[Depends(get_current_admin_user)])
def update_category(category_id: str, category: schemas.Category, db: Session = Depends(get_db)):
    db_category = crud.update_category(db=db, category_id=category_id, category=category)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


@app.delete("/categories/{category_id}", dependencies=[Depends(get_current_admin_user)])
def delete_category(category_id: str, db: Session = Depends(get_db)):
    db_category = crud.delete_category(db=db, category_id=category_id)
    if not db_category.active:
        raise HTTPException(status_code=404, detail="Category deleted")
    return db_category


@app.post("/books/", dependencies=[Depends(get_current_admin_user)])
def create_book(book: schemas.Book, db: Session = Depends(get_db)):
    return crud.create_book(db=db, book=book)


@app.get("/books/")
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_books(db=db, skip=skip, limit=limit)


@app.get("/books/{book_id}")
def read_book(book_id: str, db: Session = Depends(get_db)):
    db_book = crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.put("/books/{book_id}", dependencies=[Depends(get_current_admin_user)])
def update_book(book_id: str, book: schemas.Book, db: Session = Depends(get_db)):
    db_book = crud.update_book(db=db, book_id=book_id, book=book)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.delete("/books/{book_id}", dependencies=[Depends(get_current_admin_user)])
def delete_book(book_id: str, db: Session = Depends(get_db)):
    db_book = crud.delete_book(db=db, book_id=book_id)
    if not db_book.active:
        raise HTTPException(status_code=404, detail="Book deleted")
    return db_book
