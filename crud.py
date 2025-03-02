from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Message
from schemas import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user(db: AsyncSession, user_id: int = None, email: str = None, username: str = None):
    query = select(User)
    if user_id:
        query = query.filter(User.id == user_id)
    elif email:
        query = query.filter(User.email == email)
    elif username:
        query = query.filter(User.username == username)

    result = await db.execute(query)
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate):
    if await get_user(db, email=user.email):
        raise ValueError("Пользователь с таким email уже существует")
    if await get_user(db, username=user.username):
        raise ValueError("Пользователь с таким username уже существует")

    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, email=user.email,
                   phone_number=user.phone_number)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_telegram_chat_id(db: AsyncSession, user_id: int, chat_id: int):
    user = await get_user(db, user_id=user_id)
    if not user:
        raise ValueError("Пользователь не найден")

    user.telegram_chat_id = chat_id
    await db.commit()
    await db.refresh(user)
    return user
