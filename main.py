from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
import schemas
import auth_utils

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CampusAI Backend")

# We use a custom oauth2 scheme to pick up the token from header
# For student/admin distinction, we'll use specific dependencies
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

@app.get("/")
async def root():
    return {"message": "Backend running"}

# --- Student Routes ---

@app.post("/students/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_student(user: schemas.UserCreate, db: Session = Depends(get_db)):
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

@app.post("/students/login", response_model=schemas.Token)
def login_student(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.email == request.email).first()
    if not student or not auth_utils.verify_password(request.password, student.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = auth_utils.create_access_token(
        data={"id": student.id, "role": student.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/student/dashboard")
def student_dashboard(current_user: dict = Depends(auth_utils.check_role("student"))):
    return {
        "message": "Welcome to Student Dashboard",
        "student_id": current_user["id"],
        "role": current_user["role"]
    }

# --- Admin Routes ---

@app.post("/admins/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
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
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

@app.post("/admins/login", response_model=schemas.Token)
def login_admin(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.email == request.email).first()
    if not admin or not auth_utils.verify_password(request.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = auth_utils.create_access_token(
        data={"id": admin.id, "role": admin.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/admin/dashboard")
def admin_dashboard(current_user: dict = Depends(auth_utils.check_role("admin"))):
    return {
        "message": "Welcome to Admin Dashboard",
        "admin_id": current_user["id"],
        "role": current_user["role"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
