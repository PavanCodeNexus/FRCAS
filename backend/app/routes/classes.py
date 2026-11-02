from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Class, Teacher, Student
from ..schemas import ClassCreate, ClassResponse
from .auth import get_current_teacher

router = APIRouter(prefix="/classes", tags=["Classes"])

@router.post("", response_model=ClassResponse)
def create_class(
    cls_in: ClassCreate,
    current_teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    new_class = Class(
        subject=cls_in.subject.strip(),
        section=cls_in.section.strip().upper(),
        teacher_id=current_teacher.id
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class

@router.get("", response_model=List[ClassResponse])
def list_classes(
    current_teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    return db.query(Class).filter(Class.teacher_id == current_teacher.id).all()

@router.get("/{class_id}", response_model=ClassResponse)
def get_class(
    class_id: int,
    current_teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    cls = db.query(Class).filter(Class.id == class_id, Class.teacher_id == current_teacher.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    return cls
