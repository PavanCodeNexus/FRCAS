from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Teacher
from ..schemas import TeacherCreate, TeacherLogin, Token, TokenData
from ..utils.security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_teacher(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Teacher:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject identity",
            headers={"WWW-Authenticate": "Bearer"},
        )
    teacher = db.query(Teacher).filter(Teacher.email == email).first()
    if teacher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    return teacher

@router.post("/register", response_model=Token)
def register_teacher(teacher_in: TeacherCreate, db: Session = Depends(get_db)):
    existing = db.query(Teacher).filter(Teacher.email == teacher_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_teacher = Teacher(
        name=teacher_in.name,
        email=teacher_in.email,
        password_hash=hash_password(teacher_in.password)
    )
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)

    token = create_access_token({"sub": new_teacher.email, "name": new_teacher.name})
    return Token(
        access_token=token,
        token_type="bearer",
        teacher_name=new_teacher.name,
        teacher_email=new_teacher.email
    )

@router.post("/login", response_model=Token)
def login_teacher(login_data: TeacherLogin, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.email == login_data.email).first()
    if not teacher or not verify_password(login_data.password, teacher.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token({"sub": teacher.email, "name": teacher.name})
    return Token(
        access_token=token,
        token_type="bearer",
        teacher_name=teacher.name,
        teacher_email=teacher.email
    )

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.email == form_data.username).first()
    if not teacher or not verify_password(form_data.password, teacher.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token({"sub": teacher.email, "name": teacher.name})
    return Token(
        access_token=token,
        token_type="bearer",
        teacher_name=teacher.name,
        teacher_email=teacher.email
    )

@router.get("/me")
def get_me(current_teacher: Teacher = Depends(get_current_teacher)):
    return {
        "id": current_teacher.id,
        "name": current_teacher.name,
        "email": current_teacher.email,
        "created_at": current_teacher.created_at
    }
