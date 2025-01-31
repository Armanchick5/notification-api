from sqlalchemy.orm import Session
from models import User, Message
from schemas import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_username(db: Session, username: str):
    resp = db.query(User).filter(User.username == username).first()
    print(resp)
    return resp


def create_user(db: Session, user: UserCreate):
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


def save_message(db: Session, user_id: int, text: str):
    db_message = Message(user_id=user_id, text=text)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
