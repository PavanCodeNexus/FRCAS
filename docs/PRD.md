# PRD: Face Recognition Classroom Attendance System

**Version:** 1.0
**Status:** Draft
**Owner:** Pavan B C

---

## 1. Problem Statement

In classrooms, attendance is taken by calling out roll numbers or USNs. This takes 4-5 minutes per lecture, wastes teaching time, and frustrates lecturers. Methods where students mark their own attendance (QR, GPS, apps) can be cheated through proxy attendance.

## 2. Goal

Let a teacher take attendance for the whole class in under 1 minute by photographing the classroom. The system detects every face, matches it against pre-registered student photos, and marks attendance automatically. Because the teacher captures the photo, students cannot mark for each other.

## 3. Objectives and Success Metrics

| Objective | Metric | Target |
|---|---|---|
| Save lecturer time | Time to complete attendance | Under 60 seconds |
| Accurate recognition | Auto-match accuracy (front/middle benches) | 90% or higher |
| Low false matches | Wrong student marked present | Under 1% |
| Easy correction | Teacher can fix misses in the review screen | Under 30 seconds |
| Proxy prevention | Proxy attendance possible | None |

## 4. Users

| User | Description | Needs |
|---|---|---|
| Teacher | Takes attendance each lecture | Fast capture, easy review, export |
| Student | Registers photos once | Simple registration, privacy |
| Admin (optional) | Manages sections and teachers | Add/edit classes and users |

## 5. Scope

### In scope (MVP)
- Student registration with 3-5 face photos per USN
- Teacher login
- Upload or capture 1-3 class photos per session
- Face detection, embedding, and matching
- Review screen for unmatched or low-confidence faces
- Save attendance and export to CSV/Excel
- Basic attendance history per class

### Out of scope (MVP)
- Live video attendance
- Mobile native apps
- Parent notifications
- Integration with the college ERP/VTU portal

### Future scope
- Video sweep capture using multiple frames
- Anomaly detection (suspicious patterns)
- AWS deployment (Rekognition, S3, RDS)
- Student dashboard with attendance percentage
- Low attendance alerts

## 6. Functional Requirements

### 6.1 Student Registration
- FR1: Admin or student can add a student with USN, name, and section.
- FR2: System accepts 3-5 clear photos (front, slight left, slight right).
- FR3: System rejects photos with no face or multiple faces.
- FR4: System stores a face embedding per photo, not just the raw image.
- FR5: Student consent is recorded before photos are stored.

### 6.2 Authentication
- FR6: Teacher logs in with email and password.
- FR7: Passwords are hashed; sessions use JWT.

### 6.3 Attendance Capture
- FR8: Teacher selects class (subject and section) and starts a session.
- FR9: Teacher uploads or captures 1-3 photos of the classroom.
- FR10: System detects all faces in every photo.

### 6.4 Recognition
- FR11: Each detected face is converted to an embedding.
- FR12: Embeddings are matched against students of the selected section using cosine similarity.
- FR13: Matches above the high threshold are auto-marked present.
- FR14: Matches between the low and high thresholds go to the review list.
- FR15: Faces below the low threshold are shown as unknown.

### 6.5 Review and Confirmation
- FR16: The review screen shows detected faces with a suggested USN and confidence score.
- FR17: Teacher can confirm, change, or reject each match.
- FR18: Teacher can manually mark any absent-looking student present.
- FR19: Teacher confirms to save the final attendance.

### 6.6 Reports
- FR20: Export attendance as CSV/Excel by date, class, or student.
- FR21: View attendance history and percentage per student.

## 7. Non-Functional Requirements

| Area | Requirement |
|---|---|
| Performance | Process one class photo (60 students) in under 15 seconds |
| Accuracy | Strict threshold with teacher confirmation to avoid false matches |
| Security | Encrypted face data, hashed passwords, HTTPS, role-based access |
| Privacy | Consent, data deletion on request, compliance with India's DPDP Act 2023 |
| Usability | Works on laptop browser first; simple 3-click flow |
| Reliability | If recognition fails, manual marking still works |

## 8. Technical Approach

| Layer | Choice |
|---|---|
| Face detection | InsightFace (RetinaFace) |
| Face embedding | ArcFace (via InsightFace) |
| Matching | Cosine similarity |
| Backend | Python, FastAPI |
| Database | SQLite (MVP), PostgreSQL or AWS RDS later |
| Frontend | React (or plain HTML for first prototype) |
| Storage | Local folders (MVP), AWS S3 later |

## 9. Data Model

| Table | Fields |
|---|---|
| students | usn, name, section, consent_given, created_at |
| face_embeddings | id, usn, embedding, photo_path |
| teachers | id, name, email, password_hash |
| classes | id, subject, section, teacher_id |
| sessions | id, class_id, date, photo_paths |
| attendance | id, session_id, usn, status, confidence, method (auto/manual) |

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Small faces on back benches | Missed detections | Multiple photos from different angles, high-res camera, video frames later |
| Poor lighting, masks, side angles | Low match confidence | Review screen, multiple registration photos |
| False matches (look-alikes) | Wrong attendance | Strict threshold plus teacher confirmation |
| Privacy and biometric data concerns | Legal and trust issues | Consent form, encryption, delete on request |
| Slow processing on weak laptops | Bad experience | Resize images, CPU-friendly models, batch processing |
| Students absent but photo shows a lookalike | Rare false positive | Confidence score and review step |

## 11. Milestones

| Phase | Deliverable |
|---|---|
| Phase 1 | Python script: register faces and match one test photo (prove accuracy) |
| Phase 2 | FastAPI backend and database |
| Phase 3 | Web UI: login, register, capture, review |
| Phase 4 | Reports, accuracy tuning, deployment (AWS optional) |

## 12. Open Questions
- What camera will the teacher use (phone, webcam, classroom camera)?
- How many students per section (class size)?
- Will photos be taken once per lecture or at fixed times?
- Does the college allow storing student photos? Who approves consent?
