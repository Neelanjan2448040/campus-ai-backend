from sqlalchemy import Column, Integer, String, Float
from database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="student")
    marks = Column(Float, default=0.0)
    attendance = Column(Float, default=0.0)

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="admin")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    faculty = Column(String(255))
    batch = Column(String(255))
    students = Column(Integer, default=0)
    schedule = Column(String(255))
    assignments = Column(Integer, default=0)
    tests = Column(Integer, default=0)
    dept = Column(String(255))
    credits = Column(Integer, default=3)
