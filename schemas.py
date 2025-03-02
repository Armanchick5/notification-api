from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    phone_number: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class MessageCreate(BaseModel):
    text: str
    recipient_username: Optional[str] = None
    notification_type: str


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    recipient_id: Optional[int]
    text: str
    notification_type: str
    status: str


class TelegramBind(BaseModel):
    telegram_chat_id: int
