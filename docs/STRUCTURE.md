# Project Structure: Face Recognition Classroom Attendance System

## 1. Folder Tree

```
face-attendance/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── config.py               # thresholds, paths, settings
│   │   ├── database.py             # DB connection and session
│   │   ├── models.py               # DB tables (SQLAlchemy)
│   │   ├── schemas.py              # request/response models (Pydantic)
│   │   ├── routes/
│   │   │   ├── auth.py             # login
│   │   │   ├── students.py         # register, list, delete
│   │   │   ├── classes.py          # create/list classes
│   │   │   ├── attendance.py       # process and confirm
│   │   │   └── reports.py          # export CSV/Excel
│   │   ├── services/
│   │   │   ├── detector.py         # find faces
│   │   │   ├── embedder.py         # face → vector
│   │   │   ├── matcher.py          # cosine similarity + thresholds
│   │   │   └── report_service.py   # build CSV/Excel
│   │   └── utils/
│   │       ├── security.py         # password hashing, JWT
│   │       └── image_utils.py      # resize, orientation fix
│   ├── tests/
│   │   ├── test_detector.py
│   │   ├── test_matcher.py
│   │   └── test_api.py
│   ├── requirements.txt
│   └── .env                        # secrets (never commit)
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── RegisterStudent.jsx
│   │   │   ├── Capture.jsx
│   │   │   ├── Review.jsx
│   │   │   └── Reports.jsx
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── FaceCard.jsx        # face crop + suggested USN
│   │   │   └── UploadBox.jsx
│   │   ├── api/
│   │   │   └── client.js           # API calls
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
├── data/
│   ├── registered_faces/           # student photos (git-ignored)
│   ├── class_photos/               # test classroom images (git-ignored)
│   └── exports/                    # generated CSV/Excel
│
├── notebooks/
│   └── accuracy_experiments.ipynb  # threshold tuning
│
├── scripts/
│   └── phase1_prototype.py         # first working script
│
├── docs/
│   ├── PRD.md
│   ├── WORKFLOWS.md
│   ├── ARCHITECTURE.md
│   └── STRUCTURE.md
│
├── .gitignore
└── README.md
```

## 2. What Each Part Does

| Folder / File | Purpose |
|---|---|
| `backend/app/main.py` | Starts the FastAPI app and registers routes |
| `config.py` | HIGH/LOW thresholds, model name, file paths |
| `models.py` | Database tables |
| `routes/` | API endpoints, one file per feature |
| `services/` | The AI logic, kept separate from routes |
| `utils/` | Helper functions (security, image handling) |
| `frontend/src/pages/` | One page per screen |
| `data/` | Local photos and exports (never pushed to GitHub) |
| `notebooks/` | Experiments to measure and tune accuracy |
| `scripts/` | Standalone prototype for Phase 1 |
| `docs/` | Project documents |

## 3. Key Dependencies

**Backend (`requirements.txt`)**
```
fastapi
uvicorn
sqlalchemy
pydantic
python-multipart
python-jose
passlib[bcrypt]
insightface
onnxruntime
opencv-python
numpy
pandas
openpyxl
```

**Frontend**
```
react
react-router-dom
axios
```

## 4. .gitignore Essentials

```
.env
data/registered_faces/
data/class_photos/
data/exports/
__pycache__/
node_modules/
*.db
```

Student photos and face data must never be pushed to GitHub.

## 5. Build Order

| Phase | Files to create first |
|---|---|
| 1 | `scripts/phase1_prototype.py` |
| 2 | `database.py`, `models.py`, `services/*`, `routes/students.py`, `routes/attendance.py` |
| 3 | `frontend/src/pages/*`, `components/*` |
| 4 | `routes/reports.py`, `report_service.py`, tests, deployment |
