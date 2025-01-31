from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    password: str
    phone_number: str
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    username: str
    phone_number: str
    email: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class MessageCreate(BaseModel):
    text: str
    recipient_username: str
