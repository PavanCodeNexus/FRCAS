import json
import datetime
from typing import List, Optional
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Class, Student, Session as AttendanceSession, Attendance, Teacher
from ..schemas import (
    AttendanceProcessResult,
    AttendanceConfirmRequest,
    AttendanceConfirmResponse,
    DetectedMatch,
    StudentResponse
)
from ..services.detector import detect_faces
from ..services.matcher import match_faces_to_students
from ..utils.image_utils import bytes_to_cv2_image, resize_if_needed, crop_face, cv2_to_base64_jpeg
from .auth import get_current_teacher

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/process", response_model=AttendanceProcessResult)
async def process_classroom_photos(
    class_id: int = Form(...),
    photos: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    cls = db.query(Class).filter(Class.id == class_id, Class.teacher_id == current_teacher.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found or access denied")

    if not photos or len(photos) == 0:
        raise HTTPException(status_code=400, detail="Please upload at least 1 classroom photo.")

    # 1. Fetch all registered students and their embeddings for this section
    students = db.query(Student).filter(Student.section == cls.section).all()
    student_gallery = {}
    for s in students:
        embs = []
        for e in s.embeddings:
            try:
                emb_arr = np.array(json.loads(e.embedding_json), dtype=np.float32)
                norm = np.linalg.norm(emb_arr)
                if norm > 0:
                    emb_arr = emb_arr / norm
                embs.append(emb_arr)
            except Exception:
                continue
        if embs:
            student_gallery[s.usn] = {
                "name": s.name,
                "embeddings": embs
            }

    # 2. Detect faces in all uploaded classroom photos
    detected_faces_list = []
    for photo_idx, photo in enumerate(photos):
        content = await photo.read()
        try:
            cv_img = bytes_to_cv2_image(content)
            cv_img = resize_if_needed(cv_img, max_dimension=2560)
        except Exception as e:
            continue

        raw_faces = detect_faces(cv_img, min_det_score=0.45)
        for face in raw_faces:
            emb = face.embedding.copy()
            norm = np.linalg.norm(emb)
            if norm > 0:
                emb = emb / norm

            bbox = [int(x) for x in face.bbox]
            crop = crop_face(cv_img, bbox, margin_ratio=0.25)
            crop_b64 = cv2_to_base64_jpeg(crop, quality=80)

            detected_faces_list.append({
                "embedding": emb,
                "bbox": bbox,
                "photo_index": photo_idx,
                "crop_b64": crop_b64
            })

    # 3. Match against gallery using bipartite assignment and dual thresholds
    match_result = match_faces_to_students(detected_faces_list, student_gallery)

    # 4. Format unmatched students
    unmatched_students = []
    unmatched_set = set(match_result["unmatched_usns"])
    for s in students:
        if s.usn in unmatched_set:
            unmatched_students.append(StudentResponse(
                usn=s.usn,
                name=s.name,
                section=s.section,
                consent_given=s.consent_given,
                photo_count=len(s.embeddings),
                created_at=s.created_at
            ))

    return AttendanceProcessResult(
        total_faces_detected=len(detected_faces_list),
        auto_present=[DetectedMatch(**m) for m in match_result["auto_present"]],
        needs_review=[DetectedMatch(**m) for m in match_result["needs_review"]],
        unknown_faces=[DetectedMatch(**m) for m in match_result["unknown_faces"]],
        unmatched_students=unmatched_students
    )

@router.post("/confirm", response_model=AttendanceConfirmResponse)
def confirm_attendance(
    confirm_in: AttendanceConfirmRequest,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    cls = db.query(Class).filter(Class.id == confirm_in.class_id, Class.teacher_id == current_teacher.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    # Create new session
    session_record = AttendanceSession(
        class_id=cls.id,
        date=datetime.datetime.utcnow(),
        photo_paths=json.dumps(confirm_in.photo_paths or [])
    )
    db.add(session_record)
    db.flush()

    present_count = 0
    absent_count = 0

    for rec in confirm_in.records:
        # Check if student exists in DB; if not and name provided, create record
        student = db.query(Student).filter(Student.usn == rec.usn).first()
        if not student and rec.name:
            student = Student(
                usn=rec.usn,
                name=rec.name,
                section=cls.section,
                consent_given=True
            )
            db.add(student)
            db.flush()

        att = Attendance(
            session_id=session_record.id,
            usn=rec.usn,
            status=rec.status.upper(),
            confidence=rec.confidence,
            method=rec.method.upper()
        )
        db.add(att)
        if rec.status.upper() == "PRESENT":
            present_count += 1
        else:
            absent_count += 1

    db.commit()

    return AttendanceConfirmResponse(
        session_id=session_record.id,
        total_present=present_count,
        total_absent=absent_count,
        message=f"Attendance saved successfully. {present_count} present, {absent_count} absent."
    )

@router.get("/history/{class_id}")
def get_class_attendance_history(
    class_id: int,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher)
):
    cls = db.query(Class).filter(Class.id == class_id, Class.teacher_id == current_teacher.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")

    sessions = db.query(AttendanceSession).filter(AttendanceSession.class_id == class_id).order_by(AttendanceSession.date.desc()).all()
    history = []
    for s in sessions:
        total = len(s.attendance_records)
        present = sum(1 for a in s.attendance_records if a.status == "PRESENT")
        history.append({
            "session_id": s.id,
            "date": s.date,
            "total_students": total,
            "present_count": present,
            "absent_count": total - present,
            "attendance_rate": round((present / total * 100), 1) if total > 0 else 0
        })
    return history
