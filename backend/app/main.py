import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import BASE_DIR
from .database import engine, Base, SessionLocal
from .models import Teacher
from .utils.security import hash_password
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routes import auth, classes, students, attendance, reports

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Seed default demo teacher if none exists
def seed_default_teacher():
    db = SessionLocal()
    try:
        existing = db.query(Teacher).filter(Teacher.email == "teacher@college.edu").first()
        if not existing:
            demo_teacher = Teacher(
                name="Prof. Pavan B C",
                email="teacher@college.edu",
                password_hash=hash_password("admin123")
            )
            db.add(demo_teacher)
            db.commit()
    finally:
        db.close()

seed_default_teacher()

app = FastAPI(
    title="FRCAS - Face Recognition Classroom Attendance API",
    description="High-Accuracy Classroom Face Recognition Attendance System with Dual-Threshold Review",
    version="1.0.0"
)

# Enable CORS for web and mobile testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(auth.router)
app.include_router(classes.router)
app.include_router(students.router)
app.include_router(attendance.router)
app.include_router(reports.router)

# Mount Static & UI Assets
STATIC_DIR = Path(__file__).resolve().parent / "static"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/manifest.json")
def serve_manifest():
    manifest_file = STATIC_DIR / "manifest.json"
    if manifest_file.exists():
        return FileResponse(manifest_file, media_type="application/manifest+json")
    return {"message": "Manifest not found"}

@app.get("/sw.js")
def serve_sw():
    sw_file = STATIC_DIR / "sw.js"
    if sw_file.exists():
        return FileResponse(
            sw_file,
            media_type="application/javascript",
            headers={"Service-Worker-Allowed": "/"}
        )
    return {"message": "Service Worker not found"}

@app.get("/")
@app.get("/professor")
def serve_professor():
    prof_file = STATIC_DIR / "index.html"
    if prof_file.exists():
        return FileResponse(prof_file)
    return {"message": "Professor Portal"}

@app.get("/student")
def serve_student():
    student_file = STATIC_DIR / "student.html"
    if student_file.exists():
        return FileResponse(student_file)
    return {"message": "Student Portal"}

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
