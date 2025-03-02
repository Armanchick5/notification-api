import os
import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import crud
import schemas
from dependencies import get_db, get_current_user
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

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


@router.post("/send_message")
async def send_message(
        message: schemas.MessageCreate,
        current_user: schemas.UserResponse = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    recipient = await crud.get_user(db,
                                    username=message.recipient_username) if message.recipient_username else current_user
    if not recipient:
        raise HTTPException(status_code=400, detail="Получатель не найден")

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
            raise HTTPException(status_code=400, detail="Telegram chat ID получателя не указан.")
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": recipient.telegram_chat_id, "text": message.text}
        response = requests.post(url, json=payload)
        if not response.json().get("ok"):
            raise HTTPException(status_code=500, detail="Ошибка отправки в Telegram")

    return {"detail": "Сообщение успешно отправлено."}
