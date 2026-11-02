import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    classes = relationship("Class", back_populates="teacher", cascade="all, delete-orphan")


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(100), nullable=False)
    section = Column(String(50), index=True, nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)

    teacher = relationship("Teacher", back_populates="classes")
    sessions = relationship("Session", back_populates="cls", cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"

    usn = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    section = Column(String(50), index=True, nullable=False)
    consent_given = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    embeddings = relationship("FaceEmbedding", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")


class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    usn = Column(String(50), ForeignKey("students.usn"), nullable=False)
    embedding_json = Column(Text, nullable=False)  # JSON-encoded 512-D float array
    photo_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="embeddings")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    photo_paths = Column(Text, nullable=True)  # JSON array of photo paths

    cls = relationship("Class", back_populates="sessions")
    attendance_records = relationship("Attendance", back_populates="session", cascade="all, delete-orphan")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    usn = Column(String(50), ForeignKey("students.usn"), nullable=False)
    status = Column(String(20), default="PRESENT")  # PRESENT / ABSENT
    confidence = Column(Float, default=1.0)
    method = Column(String(20), default="AUTO")    # AUTO / MANUAL / REVIEW_CONFIRMED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("Session", back_populates="attendance_records")
    student = relationship("Student", back_populates="attendance_records")
