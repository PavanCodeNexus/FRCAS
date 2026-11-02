from typing import List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

# Auth Schemas
class TeacherCreate(BaseModel):
    name: str
    email: str
    password: str

class TeacherLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    teacher_name: str
    teacher_email: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Class Schemas
class ClassCreate(BaseModel):
    subject: str
    section: str

class ClassResponse(BaseModel):
    id: int
    subject: str
    section: str
    teacher_id: int

    class Config:
        from_attributes = True

# Student Schemas
class StudentResponse(BaseModel):
    usn: str
    name: str
    section: str
    consent_given: bool
    photo_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

# Attendance Processing Schemas
class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int

class DetectedMatch(BaseModel):
    usn: Optional[str] = None
    name: Optional[str] = None
    confidence: float
    bbox: List[int]
    photo_index: int
    face_crop_base64: Optional[str] = None

class AttendanceProcessResult(BaseModel):
    total_faces_detected: int
    auto_present: List[DetectedMatch]
    needs_review: List[DetectedMatch]
    unknown_faces: List[DetectedMatch]
    unmatched_students: List[StudentResponse]

class AttendanceRecordCommit(BaseModel):
    usn: str
    name: Optional[str] = None
    status: str = "PRESENT"  # PRESENT or ABSENT
    confidence: float = 1.0
    method: str = "AUTO"     # AUTO, MANUAL, REVIEW_CONFIRMED

class AttendanceConfirmRequest(BaseModel):
    class_id: int
    records: List[AttendanceRecordCommit]
    photo_paths: Optional[List[str]] = []

class AttendanceConfirmResponse(BaseModel):
    session_id: int
    total_present: int
    total_absent: int
    message: str
