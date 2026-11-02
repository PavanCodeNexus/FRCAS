import json
import os
from typing import List, Optional
import cv2
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Student, FaceEmbedding, Teacher
from ..schemas import StudentResponse
from ..services.detector import validate_and_extract_face
from ..config import REGISTERED_FACES_DIR
from .auth import get_current_teacher

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/self-register")
async def self_register_student(
    usn: str = Form(...),
    name: str = Form(...),
    section: str = Form(...),
    consent_given: bool = Form(True),
    photos: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Public endpoint for students to enroll their 3 facial scan angles."""
    return await _process_student_registration(usn, name, section, consent_given, photos, db)

@router.post("/register")
async def register_student(
    usn: str = Form(...),
    name: str = Form(...),
    section: str = Form(...),
    consent_given: bool = Form(True),
    photos: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_teacher: Optional[Teacher] = Depends(lambda: None)  # Optional for teacher portal
):
    return await _process_student_registration(usn, name, section, consent_given, photos, db)

async def _process_student_registration(
    usn: str,
    name: str,
    section: str,
    consent_given: bool,
    photos: List[UploadFile],
    db: Session
):
    clean_usn = usn.strip().upper()
    clean_name = name.strip()
    clean_section = section.strip().upper()

    if not clean_usn or not clean_name or not clean_section:
        raise HTTPException(status_code=400, detail="USN, name, and section are required.")

    if not consent_given:
        raise HTTPException(status_code=400, detail="Student biometric consent is required under DPDP Act.")

    if len(photos) == 0:
        raise HTTPException(status_code=400, detail="At least 1 clear photo is required (3 recommended).")

    # Check if student already exists
    student = db.query(Student).filter(Student.usn == clean_usn).first()
    if not student:
        student = Student(
            usn=clean_usn,
            name=clean_name,
            section=clean_section,
            consent_given=consent_given
        )
        db.add(student)
        db.flush()
    else:
        # Update existing student's name/section
        student.name = clean_name
        student.section = clean_section
        student.consent_given = consent_given

    valid_embeddings_count = 0
    errors = []

    for idx, photo in enumerate(photos):
        try:
            content = await photo.read()
            is_valid, msg, emb, face_crop = validate_and_extract_face(content)

            if not is_valid:
                errors.append(f"Photo {idx+1} ({photo.filename}): {msg}")
                continue

            # Save face crop image
            photo_filename = f"{clean_usn}_pose_{idx+1}.jpg"
            photo_filepath = REGISTERED_FACES_DIR / photo_filename
            cv2.imwrite(str(photo_filepath), face_crop)

            # Save embedding
            face_emb_record = FaceEmbedding(
                usn=clean_usn,
                embedding_json=json.dumps(emb.tolist()),
                photo_path=str(photo_filepath)
            )
            db.add(face_emb_record)
            valid_embeddings_count += 1
        except Exception as e:
            errors.append(f"Photo {idx+1} failed to process: {str(e)}")

    if valid_embeddings_count == 0:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Registration failed. None of the uploaded photos were valid: {'; '.join(errors)}"
        )

    db.commit()
    return {
        "status": "success",
        "usn": clean_usn,
        "name": clean_name,
        "section": clean_section,
        "valid_photos_saved": valid_embeddings_count,
        "warnings": errors
    }

@router.get("", response_model=List[StudentResponse])
def list_students(
    section: Optional[str] = None,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    query = db.query(Student)
    if section:
        query = query.filter(Student.section == section.strip().upper())
    
    students = query.order_by(Student.usn).all()
    results = []
    for s in students:
        results.append(StudentResponse(
            usn=s.usn,
            name=s.name,
            section=s.section,
            consent_given=s.consent_given,
            photo_count=len(s.embeddings),
            created_at=s.created_at
        ))
    return results

@router.delete("/{usn}")
def delete_student(
    usn: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    clean_usn = usn.strip().upper()
    student = db.query(Student).filter(Student.usn == clean_usn).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Delete physical photo crops
    for emb in student.embeddings:
        if emb.photo_path and os.path.exists(emb.photo_path):
            try:
                os.remove(emb.photo_path)
            except OSError:
                pass

    db.delete(student)
    db.commit()
    return {"message": f"Student {clean_usn} and all associated biometric data permanently deleted."}
