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
    user: UserResponse

class TokenData(BaseModel):
    id: Optional[int] = None
    role: Optional[str] = None

class CourseBase(BaseModel):
    code: str
    name: str
    faculty: Optional[str] = ""
    batch: Optional[str] = ""
    students: Optional[int] = 0
    schedule: Optional[str] = ""
    assignments: Optional[int] = 0
    tests: Optional[int] = 0
    dept: Optional[str] = ""
    credits: Optional[int] = 3

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int

    class Config:
        from_attributes = True
