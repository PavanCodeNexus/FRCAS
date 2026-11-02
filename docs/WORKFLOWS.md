# Workflows: Face Recognition Classroom Attendance System

This file describes how each part of the system works, step by step.

---

## 1. Student Registration Workflow

**Actor:** Student or Admin

```
Start
  ↓
Enter USN, name, section
  ↓
Show consent form → Student agrees?
  ├─ No → Stop (no data stored)
  └─ Yes
       ↓
Upload 3-5 photos (front, left, right)
  ↓
Detect face in each photo
  ↓
Exactly 1 face found?
  ├─ No → Reject photo, ask to retake
  └─ Yes
       ↓
Generate embedding (ArcFace)
  ↓
Save embeddings + photo path linked to USN
  ↓
Registration complete
```

**Rules**
- Photo must be clear, well-lit, no sunglasses or heavy filters
- Reject blurry photos and photos with 0 or 2+ faces
- Store embeddings, and encrypt stored photos

---

## 2. Teacher Login Workflow

```
Open app → Enter email + password
  ↓
Backend checks hashed password
  ├─ Wrong → Show error
  └─ Correct → Issue JWT token → Open dashboard
```

---

## 3. Attendance Session Workflow (Main Flow)

**Actor:** Teacher

```
Dashboard → Select class (subject + section)
  ↓
Start attendance session
  ↓
Upload / capture 1-3 class photos
  ↓
Backend: preprocess images (resize, fix orientation)
  ↓
Detect all faces in every photo
  ↓
For each face:
   Generate embedding
   Compare with embeddings of that section's students
   Find best match + similarity score
  ↓
Apply thresholds (see section 4)
  ↓
Show result summary:
   ✅ Auto-marked present
   ⚠️ Needs review
   ❓ Unknown faces
   ❌ Not detected (likely absent)
  ↓
Teacher goes to Review screen (section 5)
  ↓
Teacher confirms → Attendance saved
  ↓
Export / view report
```

---

## 4. Recognition and Threshold Logic

```
similarity = cosine_similarity(face_embedding, student_embedding)

if similarity >= HIGH_THRESHOLD (e.g. 0.60):
    → Auto-mark PRESENT
elif similarity >= LOW_THRESHOLD (e.g. 0.40):
    → Send to REVIEW list (suggested USN shown)
else:
    → UNKNOWN face
```

**Notes**
- Thresholds are starting values only. Tune them using real test photos.
- If the same USN matches two faces, keep the higher score and flag the other for review.
- Each face can match only one USN, and each USN is counted once per session.
- Use the best score across all uploaded photos of the session.

---

## 5. Review and Correction Workflow

```
Review screen opens
  ↓
Show face crops with suggested USN + confidence
  ↓
For each item, teacher can:
   • Confirm   → mark present
   • Change    → pick correct USN from the list
   • Reject    → ignore (not a student / wrong match)
  ↓
Show list of students NOT detected
  ↓
Teacher can manually mark any as present (e.g. face hidden)
  ↓
Press "Save Attendance"
  ↓
Each record saved with method = auto / manual
```

---

## 6. Save and Report Workflow

```
Save attendance
  ↓
Write records: session_id, usn, status, confidence, method
  ↓
Reports available:
   • Export CSV/Excel for a date or class
   • Student-wise attendance percentage
   • Low attendance list (below 75%)
```

---

## 7. System-Level Data Flow

```
Browser (React)
   │  upload photos
   ▼
FastAPI backend
   ├─ detector.py  → find faces
   ├─ embedder.py  → face → vector
   └─ matcher.py   → cosine similarity + thresholds
   │
   ▼
Database (SQLite → PostgreSQL / AWS RDS)
   │
   ▼
Review UI → Confirmed attendance → Export
```

---

## 8. Error and Edge Case Handling

| Situation | System behavior |
|---|---|
| No faces detected in photo | Ask teacher to retake from a better angle |
| Photo too dark or blurry | Warn teacher before processing |
| Face matches two students closely | Send to review, do not auto-mark |
| Student not registered | Show as unknown, teacher can mark manually |
| Backend or model fails | Fall back to manual attendance list |
| Duplicate session for the same class and date | Ask to overwrite or cancel |
| Teacher uploads wrong section | Allow changing section before processing |

---

## 9. Privacy and Security Workflow

```
Consent collected at registration
  ↓
Face data encrypted at rest, HTTPS in transit
  ↓
Only teachers of that class can view results
  ↓
Class photos auto-deleted after processing (or after X days)
  ↓
Student can request deletion → embeddings + photos removed
```

---

## 10. Development Workflow (Build Order)

| Phase | Task | Done when |
|---|---|---|
| 1 | Script: register faces from a folder, match one test photo | Correct names printed for test photo |
| 2 | FastAPI: register, match, and save endpoints + SQLite | Endpoints work in Swagger UI |
| 3 | Web UI: login, register, capture, review | Full flow works end to end |
| 4 | Reports, threshold tuning, security, deployment | Tested on a real classroom photo |

**Testing checklist**
- Test with 10, then 30, then full class size
- Test different lighting, seating positions, and distances
- Record accuracy: correct matches, misses, and false matches
- Adjust thresholds based on results
