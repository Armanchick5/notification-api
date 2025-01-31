from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
import crud, models, schemas
import asyncio
from database import engine
from auth import create_access_token
from dependencies import get_db, get_current_user
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from twilio.rest import Client
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    # MAIL_TLS=True,
    # MAIL_SSL=False,
)
mail = FastMail(conf)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)


@app.post("/token", response_model=schemas.Token)
def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not crud.pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/send_message")
def send_message(
    message: schemas.MessageCreate,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    crud.save_message(db, current_user.id, message.text)
    print(message.text)
    recipient = crud.get_user_by_username(db, username=message.recipient_username)
    if not recipient:
        raise HTTPException(status_code=400)
    print(recipient.email)

    email_message = MessageSchema(
        subject="Новое сообщение",
        recipients=[recipient.email],
        body=message.text,
        subtype="plain",
    )
    asyncio.run(mail.send_message(email_message))

    # twilio_client.messages.create(
    #     body=message.text,
    #     from_=TWILIO_PHONE_NUMBER,
    #     to=current_user.phone_number,
    # )

    return {"detail": "Сообщение отправлено"}