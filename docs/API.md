# FaceMark (FRCAS) - REST API Documentation

This document describes all API endpoints exposed by the FaceMark FastAPI backend.

**Base URL:** `http://localhost:8000`  
**Interactive Swagger UI:** `http://localhost:8000/docs`  
**ReDoc Reference:** `http://localhost:8000/redoc`

---

## 1. Authentication (`/auth`)

### `POST /auth/register`
Register a new faculty / teacher account.
* **Request Body (JSON):**
  ```json
  {
    "name": "Prof. Alan Turing",
    "email": "turing@college.edu",
    "password": "securepassword123"
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "teacher_name": "Prof. Alan Turing",
    "teacher_email": "turing@college.edu"
  }
  ```

### `POST /auth/login`
Authenticate faculty and obtain a JWT bearer token.
* **Request Body (JSON):**
  ```json
  {
    "email": "teacher@college.edu",
    "password": "admin123"
  }
  ```
* **Response (200 OK):** JWT Access token and teacher identity.

---

## 2. Classes & Sections (`/classes`)
*Headers required:* `Authorization: Bearer <token>`

### `GET /classes`
List all classes/sections created by the authenticated faculty member.

### `POST /classes`
Create a new academic subject and section.
* **Request Body (JSON):**
  ```json
  {
    "subject": "Data Structures & Algorithms",
    "section": "3D"
  }
  ```

### `GET /classes/{class_id}`
Retrieve details for a specific class ID.

---

## 3. Student Registration & Roster (`/students`)

### `POST /students/self-register` (Public)
Public endpoint called by the Student Face Scanner portal. Does not require teacher authentication.
* **Content-Type:** `multipart/form-data`
* **Form Fields:**
  * `usn` (string): University Seat Number (e.g. `1DT25CS206`)
  * `name` (string): Full Student Name
  * `section` (string): Class Section (e.g. `3D`)
  * `consent_given` (boolean): `true` (DPDP Act 2023 compliance)
  * `photos` (file[]): 3 live camera frames (Center, Left ~20°, Right ~20°)
* **Response:**
  ```json
  {
    "status": "success",
    "usn": "1DT25CS206",
    "name": "Pavan B C",
    "section": "3D",
    "valid_photos_saved": 3,
    "warnings": []
  }
  ```

### `GET /students?section={section}`
*Requires teacher authentication.* Lists all students registered in a section with enrolled pose count.

### `DELETE /students/{usn}`
*Requires teacher authentication.* Permanently erases student records and biometric embedding vectors for DPDP Act 2023 "Right to be Forgotten" compliance.

---

## 4. Attendance Workflow (`/attendance`)
*Headers required:* `Authorization: Bearer <token>`

### `POST /attendance/process`
Runs RetinaFace face detection and ArcFace cosine similarity matching across unlimited snapped classroom photos.
* **Content-Type:** `multipart/form-data`
* **Form Fields:**
  * `class_id` (int): Target Class ID
  * `photos` (file[]): 1 to N high-resolution room photos
* **Response (JSON):**
  * `total_faces_detected` (int)
  * `auto_present` (list): Matches with $\text{similarity} \ge 0.60$
  * `needs_review` (list): Borderline matches with $0.40 \le \text{similarity} < 0.60$
  * `unknown_faces` (list): Faces with $\text{similarity} < 0.40$
  * `unmatched_students` (list): Enrolled section students not seen in any photo

### `POST /attendance/confirm`
Commits verified attendance records to the database.
* **Request Body (JSON):**
  ```json
  {
    "class_id": 1,
    "records": [
      {
        "usn": "1DT25CS206",
        "name": "Pavan B C",
        "status": "PRESENT",
        "confidence": 0.857,
        "method": "AUTO"
      },
      {
        "usn": "1DT25CS207",
        "name": "Yashas",
        "status": "PRESENT",
        "confidence": 1.0,
        "method": "MANUAL_OVERRIDE"
      }
    ]
  }
  ```

### `GET /attendance/history/{class_id}`
Returns all past session attendance summaries for a class.

---

## 5. Reports & Exports (`/reports`)

### `GET /reports/session/{session_id}/excel`
Downloads formatted multi-sheet `.xlsx` workbook.
* **Auth:** Supports either `Authorization: Bearer <token>` header **or** `?token=<token>` query string.
* **Workbook Structure:**
  * **Sheet 1:** Session attendance with color coding and verification method.
  * **Sheet 2:** Cumulative semester attendance summary with $<75\%$ shortage alerts.

### `GET /reports/session/{session_id}/csv`
Downloads comma-separated values (`.csv`) export for ERP integration.
