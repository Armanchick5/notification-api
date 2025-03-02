from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(128))
    phone_number = Column(String(11), unique=True, nullable=True)
    email = Column(String(50), unique=True, index=True)
    role = Column(String(30), default="user")
    telegram_chat_id = Column(BigInteger, unique=True, nullable=True)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    text = Column(String(256))
    notification_type = Column(String(50), default="service")
    status = Column(String(30), default="unread")
