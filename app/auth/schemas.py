from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    full_name: str
    user_type: bool = 0


class UserResponse(BaseModel):
    user_id: int
    email: str
    full_name: str