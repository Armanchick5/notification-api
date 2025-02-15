import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
import crud, models, schemas
from database import engine
from auth import create_access_token
from dependencies import get_db, get_current_user
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import requests  # Для Telegram API
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Конфигурация FastAPI-Mail
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS") == "True",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS") == "True",
    USE_CREDENTIALS=True
)
mail = FastMail(conf)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/token", response_model=schemas.Token)
def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.email)
    if not user or not crud.pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}


class TelegramBind(BaseModel):
    telegram_chat_id: str


@app.post("/bind_telegram")
async def bind_telegram(
        bind_data: TelegramBind,
        current_user: schemas.UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, username=current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.telegram_chat_id = bind_data.telegram_chat_id
    db.commit()
    db.refresh(user)
    return {"detail": "Your telegram chat ID", "telegram_chat_id": user.telegram_chat_id}


@app.post("/send_message")
async def send_message(
        message: schemas.MessageCreate,
        current_user: schemas.UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    if not message.recipient_username:
        recipient = current_user
    else:
        recipient = crud.get_user_by_username(db, username=message.recipient_username)
        if not recipient:
            raise HTTPException(status_code=400, detail="Получатель не найден")
        if current_user.role != "admin" and recipient.username != current_user.username:
            raise HTTPException(status_code=403, detail="Недостаточно прав")

    # message_obj = crud.save_message(db, current_user.id, recipient.id, message.text, message.notification_type)

    if message.notification_type == "email":
        email_message = MessageSchema(
            subject="Новое сообщение",
            recipients=[recipient.email],
            body=message.text,
            subtype="plain",
        )
        await mail.send_message(email_message)
    elif message.notification_type == "telegram":
        if not recipient.telegram_chat_id:
            raise HTTPException(
                status_code=400,
                detail="Telegram chat ID получателя не указан."
            )
        telegram_message = f"📩 Сообщение от @{current_user.username}: {message.text}"
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": recipient.telegram_chat_id, "text": telegram_message}
        response = requests.post(url, json=payload)
        response_data = response.json()
        if not response_data.get("ok"):
            raise HTTPException(status_code=500, detail=f"Ошибка Telegram API: {response_data.get('description')}")
    return {"detail": "Сообщение успешно отправлено."}


@app.get("/messages", response_model=List[schemas.MessageResponse])
async def get_messages(
        current_user: schemas.UserResponse = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return crud.get_messages_for_user(db, current_user.id)
