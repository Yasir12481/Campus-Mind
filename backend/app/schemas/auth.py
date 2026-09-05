from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.STUDENT
    student_id: Optional[str] = None
    department: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    student_id: Optional[str] = None
    department: Optional[str] = None

    class Config:
        from_attributes = True
