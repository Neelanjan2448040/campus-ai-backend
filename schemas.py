from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    marks: Optional[float] = 0.0
    attendance: Optional[float] = 0.0

    class Config:
        from_attributes = True

class StudentUpdateMarks(BaseModel):
    marks: float

class StudentUpdateAttendance(BaseModel):
    attendance: float

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None
    role: Optional[str] = None
