import os
import auth
import models
import schemas
import crud
import g4f
import tiktoken
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from models import Base, User
from database import engine, session_scope
from auth import (authenticate_user, create_access_token, get_current_user, get_current_admin_user, get_password_hash,
                  get_db)
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv
from mangum import Mangum
from email_validator import validate_email, EmailNotValidError
from g4f.client import Client

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MyAwesomeApp")
load_dotenv()

client = Client()

def input_length(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(text))
    return num_tokens

def response(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": text}],
    )
    # print(response.choices[0].message.content)
    return response.choices[0].message.content

def chunking(text):
    size_chunk = 100
    prompt = """
                Summarize this message in 10-20 words
                """
    chunks = [text[i:i + size_chunk] for i in range(0, len(text), size_chunk)]
    chunks.append(prompt)
    # print(chunks)
    result = []
    for chunk in chunks:
        result.append(response(chunk))
    return response(result)


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
    user_role = db.query(models.User).filter(models.User.username == form_data.username).first()
    return schemas.Token(access_token=access_token, token_type="bearer", role=user_role.role)

@app.get("/users/{user_id}/{access_token}")
async def verify_email(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.is_verified(db, user_id)
    if db_user:
        return {"message": "Email verified successfully", "user": db_user}
    else:
        raise HTTPException(status_code=404, detail="User not found or already verified")

# @app.post("/send-email")
# async def send_email(email_data: schemas.EmailSchema):
#     try:
#         # Create the email message
#         msg = MIMEMultipart()
#         msg['From'] = EMAIL_ADDRESS
#         msg['To'] = email_data.email
#         msg['Subject'] = 'Email Verification'
#         msg.attach(MIMEText('Please verify your email.', 'url'))
#
#         # Connect to the Gmail SMTP server
#         server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
#         server.starttls()
#         server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#
#         # Send the email
#         server.send_message(msg)
#         server.quit()
#
#         return {"message": "Email sent successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@app.post("/signup")
async def create_user(user: schemas.User, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    try:
        valid_email = validate_email(user.email)
    except EmailNotValidError as e:
        print(str(e))
    db_user = User(username=user.username, password_hash=hashed_password, email=user.email, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token_expires = timedelta(minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30)))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    schemas.Token(access_token=access_token, token_type="bearer", role=user.role)
    await auth.send_email(db, db_user, access_token)
    return db_user


@app.get("/users")
async def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/authors", dependencies=[Depends(get_current_admin_user)])
async def create_author(author: schemas.Author, db: Session = Depends(get_db)):
    return crud.create_author(db=db, author=author)


@app.get("/authors")
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
        raise HTTPException(status_code=404, detail="Author not found")
    return db_author


@app.delete("/authors/{author_id}", dependencies=[Depends(get_current_admin_user)])
async def delete_author(author_id: str, db: Session = Depends(get_db)):
    db_author = crud.delete_author(db=db, author_id=author_id)
    if not db_author.active:
        raise HTTPException(status_code=404, detail="Author already deleted")
    return db_author


@app.post("/categories", dependencies=[Depends(get_current_admin_user)])
async def create_category(category: schemas.Category, db: Session = Depends(get_db)):
    return crud.create_category(db=db, category=category)


@app.get("/categories")
async def read_categories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_categories(db=db, skip=skip, limit=limit)


@app.get("/categories/{category_id}")
async def read_category(category_id: str, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


@app.put("/categories/{category_id}", dependencies=[Depends(get_current_admin_user)])
async def update_category(category_id: str, category: schemas.Category, db: Session = Depends(get_db)):
    db_category = crud.update_category(db=db, category_id=category_id, category=category)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


@app.delete("/categories/{category_id}", dependencies=[Depends(get_current_admin_user)])
async def delete_category(category_id: str, db: Session = Depends(get_db)):
    db_category = crud.delete_category(db=db, category_id=category_id)
    if not db_category.active:
        raise HTTPException(status_code=404, detail="Category deleted")
    return db_category


@app.post("/books", dependencies=[Depends(get_current_admin_user)])
async def create_book(book: schemas.Book, db: Session = Depends(get_db)):
    return crud.create_book(db=db, book=book)


@app.get("/books")
async def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_books(db=db, skip=skip, limit=limit)


@app.get("/books/{book_id}")
async def read_book(book_id: str, db: Session = Depends(get_db)):
    db_book = crud.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.put("/books/{book_id}", dependencies=[Depends(get_current_admin_user)])
async def update_book(book_id: str, book: schemas.Book, db: Session = Depends(get_db)):
    db_book = crud.update_book(db=db, book_id=book_id, book=book)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.delete("/books/{book_id}", dependencies=[Depends(get_current_admin_user)])
async def delete_book(book_id: str, db: Session = Depends(get_db)):
    db_book = crud.delete_book(db=db, book_id=book_id)
    if not db_book.active:
        raise HTTPException(status_code=404, detail="Book deleted")
    return db_book

@app.post("/sessions")
async def create_session(session: schemas.Session, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    session = crud.create_session(db, session, current_user)
    return session

@app.get("/sessions/{session_name}")
async def get_session(session_name: str, db: Session = Depends(get_db)):
    db_session = crud.get_session(db, name=session_name)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_session


@app.get("/sessions")
async def read_sessions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_user_session(db=db, skip=skip, limit=limit)

@app.get("/chat/{session_id}")
async def fetch_chat(session_id: str, db: Session = Depends(get_db)):
    chats = crud.get_chat(db, session_id)
    if chats is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return chats

@app.post("/chat/{prompt}")
async def response_message(chat: schemas.Chats, db: Session = Depends(get_db)):
    chat_dict = chat.dict()
    # text = "SHITPPVFNVCW
    chats = crud.get_chat(db, chat_dict["session_id"])
    chat_history = ""
    if chats:
        for chat in chats:
            chat_history += f"{chat['receive']}\n"

    if input_length(chat_history) > 500:
        print("I am here!!!")
        chat_history = chunking(chat_history)
        chat_history += chat_dict["sent"]
    else:
        chat_history += chat_dict["sent"]
        chat_history += """
                            Provide the shortest response in english"""
    receive = response(chat_history)
    chat_dict["receive"] = receive
    message = models.Chats(**chat_dict)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

handler = Mangum(app)