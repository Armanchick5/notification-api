from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import crud
import schemas
from dependencies import get_db, get_current_user

router = APIRouter()


@router.post("/bind_telegram")
async def bind_telegram(
        bind_data: schemas.TelegramBind,
        current_user: schemas.UserResponse = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        user = await crud.update_telegram_chat_id(db, user_id=current_user.id, chat_id=bind_data.telegram_chat_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"detail": "Telegram chat ID успешно привязан", "telegram_chat_id": user.telegram_chat_id}
