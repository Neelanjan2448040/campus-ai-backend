from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import engine, Base, get_db
import models
import schemas
import auth_utils
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    # Seed default courses if table is empty
    db = next(get_db())
    if db.query(models.Course).count() == 0:
        default_courses = [
            models.Course(code='CS301', name='Advanced DSA', faculty='Dr. Rajesh Kumar', batch='CSE - 3rd Year', students=64, schedule='Mon, Wed (9:00 AM)', assignments=4, tests=2, credits=4, dept='CSE'),
            models.Course(code='CS102', name='Programming in C', faculty='Mrs. Soundarya M.', batch='ECE - 1st Year', students=72, schedule='Tue, Thu (11:00 AM)', assignments=2, tests=1, credits=3, dept='ECE')
        ]
        db.add_all(default_courses)
        db.commit()
        logger.info("Default courses seeded successfully")
except Exception as e:
    logger.error(f"Error initializing database: {e}")

app = FastAPI(
    title="CampusAI Backend",
    description="A stable and production-ready API for Campus Management",
    version="1.0.0"
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )

# CORS Configuration
origins = ["*"] # Flexible for Railway/Netlify deployment

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["General"])
async def root():
    return {"status": "ok", "message": "CampusAI Backend is stable and running"}

# --- Student Routes ---

@app.post("/students/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Students"])
def register_student(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Check if email already exists
    db_user = db.query(models.Student).filter(models.Student.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Hash password exactly once
    hashed_pwd = auth_utils.hash_password(user.password)
    
    # 3. Create student (marks and attendance default to 0 in models)
    new_student = models.Student(
        name=user.name,
        email=user.email,
        password=hashed_pwd
    )
    
    try:
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return new_student
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not register student. Email may already exist.")
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Error saving data to database")

@app.post("/students/login", response_model=schemas.Token, tags=["Students"])
def login_student(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    # 1. Fetch user by email
    student = db.query(models.Student).filter(models.Student.email == request.email).first()
    
    # 2. Validate email and password (using pwd_context.verify exactly once)
    if not student or not auth_utils.verify_password(request.password, student.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # 3. Generate JWT token (1-hour expiry handled in auth_utils)
    access_token = auth_utils.create_access_token(
        data={"id": student.id, "role": student.role}
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": student
    }

@app.get("/students/details", response_model=schemas.UserResponse, tags=["Students"])
def get_student_profile(db: Session = Depends(get_db), current_user: dict = Depends(auth_utils.get_current_user_data)):
    student = db.query(models.Student).filter(models.Student.id == current_user["id"]).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# --- Admin Routes ---

@app.post("/admins/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Admins"])
def register_admin(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.Admin).filter(models.Admin.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = auth_utils.hash_password(user.password)
    new_admin = models.Admin(
        name=user.name,
        email=user.email,
        password=hashed_pwd
    )
    
    try:
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        return new_admin
    except Exception as e:
        db.rollback()
        logger.error(f"Admin registration error: {e}")
        raise HTTPException(status_code=500, detail="Error saving admin to database")

@app.post("/admins/login", response_model=schemas.Token, tags=["Admins"])
def login_admin(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.email == request.email).first()
    if not admin or not auth_utils.verify_password(request.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = auth_utils.create_access_token(
        data={"id": admin.id, "role": admin.role}
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": admin
    }

@app.post("/leaves/apply", tags=["General"])
def apply_leave(request: dict, current_user: dict = Depends(auth_utils.get_current_user_data)):
    # Simulating leave application storage
    logger.info(f"Leave applied by {current_user['role']} ID: {current_user['id']}: {request}")
    return {"message": "Leave application submitted successfully"}

# --- Protected Admin Operations ---

@app.get("/admin/student/{student_id}", response_model=schemas.UserResponse, tags=["Admin Operations"])
def get_student_details(student_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth_utils.check_role("admin"))):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.get("/admin/students", response_model=list[schemas.UserResponse], tags=["Admin Operations"])
def list_students(db: Session = Depends(get_db), current_user: dict = Depends(auth_utils.check_role("admin"))):
    return db.query(models.Student).all()

# --- Course Routes ---

@app.get("/courses", response_model=list[schemas.CourseResponse], tags=["Courses"])
def list_courses(db: Session = Depends(get_db)):
    return db.query(models.Course).all()

@app.post("/courses", response_model=schemas.CourseResponse, tags=["Courses"])
def add_course(course: schemas.CourseCreate, db: Session = Depends(get_db), current_user: dict = Depends(auth_utils.check_role("admin"))):
    db_course = models.Course(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@app.post("/courses/assignment/{course_code}", tags=["Courses"])
def create_assignment(course_code: str, db: Session = Depends(get_db), current_user: dict = Depends(auth_utils.check_role("admin"))):
    course = db.query(models.Course).filter(models.Course.code == course_code).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    course.assignments += 1
    db.commit()
    db.refresh(course)
    return {"message": "Assignment created", "assignments": course.assignments}

@app.post("/admin/add-student", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, tags=["Admin Operations"])
def admin_add_student(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: dict = Depends(auth_utils.check_role("admin"))):
    # This mirrors student registration but restricted to admins
    db_user = db.query(models.Student).filter(models.Student.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = auth_utils.hash_password(user.password)
    new_student = models.Student(
        name=user.name,
        email=user.email,
        password=hashed_pwd
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@app.put("/admin/update-marks/{student_id}", response_model=schemas.UserResponse, tags=["Admin Operations"])
def update_marks(student_id: int, request: schemas.StudentUpdateMarks, db: Session = Depends(get_db), current_user: dict = Depends(auth_utils.check_role("admin"))):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        student.marks = request.marks
        db.commit()
        db.refresh(student)
        return student
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating marks")

@app.put("/admin/update-attendance/{student_id}", response_model=schemas.UserResponse, tags=["Admin Operations"])
def update_attendance(student_id: int, request: schemas.StudentUpdateAttendance, db: Session = Depends(get_db), current_user: dict = Depends(auth_utils.check_role("admin"))):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        student.attendance = request.attendance
        db.commit()
        db.refresh(student)
        return student
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating attendance")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
