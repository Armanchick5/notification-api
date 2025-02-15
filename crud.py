from sqlalchemy.orm import Session
from models import User, Message
from schemas import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate):
    if db.query(User).count() >= 100:
        raise ValueError("Достигнут лимит пользователей (100)")
    if get_user_by_email(db, user.email):
        raise ValueError("Пользователь с таким email уже существует")
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        phone_number=user.phone_number,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def save_message(db: Session, sender_id: int, recipient_id: int, text: str, notification_type: str):
    if db.query(Message).count() >= 50:
        raise ValueError("Достигнут лимит сообщений (50)")
    db_message = Message(
        sender_id=sender_id,
        recipient_id=recipient_id,
        text=text,
        notification_type=notification_type
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_messages_for_user(db: Session, user_id: int):
    return db.query(Message).filter(Message.recipient_id == user_id).all()
