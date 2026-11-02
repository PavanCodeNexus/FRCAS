# Architecture: Face Recognition Classroom Attendance System

## 1. Overview

A teacher uploads classroom photos through a web app. The backend detects faces, converts them to embeddings, matches them against registered students, and returns results for the teacher to review and save.

## 2. High-Level Architecture

```
┌──────────────────────────────────────────────┐
│                 CLIENT LAYER                 │
│        React Web App (Teacher / Admin)       │
│  Login | Register | Capture | Review | Reports│
└──────────────────────┬───────────────────────┘
                       │ HTTPS (REST API + JWT)
┌──────────────────────▼───────────────────────┐
│                 API LAYER                    │
│                FastAPI Backend               │
│   auth routes | student routes | attendance  │
└───────┬─────────────────────────┬────────────┘
        │                         │
┌───────▼─────────────┐   ┌───────▼────────────┐
│     AI SERVICES     │   │    DATA LAYER      │
│  detector.py        │   │  SQLite/PostgreSQL │
│  embedder.py        │   │  File storage      │
│  matcher.py         │   │  (photos)          │
│  (InsightFace)      │   │                    │
└─────────────────────┘   └────────────────────┘
```

## 3. Components

| Component | Responsibility | Technology |
|---|---|---|
| Frontend | UI for login, registration, capture, review, reports | React |
| API server | Handles requests, auth, validation, business logic | FastAPI |
| Detector | Finds all faces in an image | InsightFace (RetinaFace) |
| Embedder | Converts a face to a numeric vector | ArcFace |
| Matcher | Compares vectors using cosine similarity, applies thresholds | NumPy |
| Database | Students, embeddings, classes, sessions, attendance | SQLite (MVP), PostgreSQL later |
| File storage | Registered photos and class photos | Local folders (MVP), AWS S3 later |
| Auth | Login and access control | JWT, bcrypt |

## 4. Request Flows

### 4.1 Student Registration
```
Client → POST /students/register (USN, photos, consent)
   → API validates input
   → Detector checks exactly 1 face per photo
   → Embedder creates embeddings
   → DB saves student + embeddings; storage saves photos
   → Response: success
```

### 4.2 Take Attendance
```
Client → POST /attendance/process (class_id, photos)
   → API loads embeddings of that section from DB
   → Detector finds all faces
   → Embedder creates embedding per face
   → Matcher compares and applies thresholds
   → Response: present / needs review / unknown lists
```

### 4.3 Confirm Attendance
```
Client → POST /attendance/confirm (session_id, final list)
   → API saves attendance records (auto/manual)
   → Response: saved
Client → GET /reports/export → CSV/Excel
```

## 5. API Endpoints (planned)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /auth/login | Teacher login |
| POST | /students/register | Add student and face photos |
| GET | /students?section= | List students |
| DELETE | /students/{usn} | Delete student data |
| POST | /classes | Create class |
| POST | /attendance/process | Detect and match faces in class photos |
| POST | /attendance/confirm | Save final attendance |
| GET | /attendance/history | Past sessions |
| GET | /reports/export | Download CSV/Excel |

## 6. Database Schema

```
students(usn PK, name, section, consent_given, created_at)
face_embeddings(id PK, usn FK, embedding, photo_path)
teachers(id PK, name, email, password_hash)
classes(id PK, subject, section, teacher_id FK)
sessions(id PK, class_id FK, date, photo_paths)
attendance(id PK, session_id FK, usn FK, status, confidence, method)
```

## 7. Matching Logic

```
score = cosine_similarity(face_vector, student_vector)

score >= HIGH  → auto present
score >= LOW   → review list
else           → unknown
```

Thresholds live in `config.py` and are tuned with real test photos.

## 8. Security Design

- Passwords hashed with bcrypt, sessions use JWT
- HTTPS for all traffic
- Embeddings and photos encrypted at rest
- Role-based access: teachers see only their classes
- Class photos deleted after processing
- Consent stored per student, deletion on request (DPDP Act 2023)

## 9. Deployment

| Stage | Setup |
|---|---|
| Local MVP | FastAPI + SQLite + React on one laptop |
| Cloud (later) | AWS EC2 or Lambda for API, RDS for DB, S3 for photos, optional Rekognition |

## 10. Scalability Notes

- Match only against the selected section, not the whole college
- Resize images before detection to save time
- Store embeddings in memory per session for faster matching
- Move heavy processing to a background worker if classes get large
