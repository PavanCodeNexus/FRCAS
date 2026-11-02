# Project Structure: Face Recognition Classroom Attendance System (FaceMark FRCAS)

## 1. Folder Tree

```text
FRCAS/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, static mounts & /health keep-alive
│   │   ├── config.py            # Paths, thresholds, JWT & model settings
│   │   ├── database.py          # SQLAlchemy SQLite connection & sessionmaker
│   │   ├── models.py            # Teacher, Class, Student, FaceEmbedding, Session, Attendance
│   │   ├── schemas.py           # Pydantic request/response validation schemas
│   │   ├── routes/              # Modular API endpoints
│   │   │   ├── attendance.py    # Multi-sector upload, matching & finalization
│   │   │   ├── auth.py          # Teacher login & JWT token issuing
│   │   │   ├── classes.py       # Course & section management
│   │   │   ├── reports.py       # Multi-sheet Excel & CSV exports
│   │   │   └── students.py      # Student self-enrollment & face registration
│   │   ├── services/            # Core AI & business logic
│   │   │   ├── detector.py      # RetinaFace face detection (InsightFace)
│   │   │   ├── embedder.py      # ArcFace 512-D feature vector extraction
│   │   │   ├── matcher.py       # Cosine similarity & dual-threshold bipartite assignment
│   │   │   └── report_service.py# OpenPyXL multi-sheet Excel generator (<75% shortage alert)
│   │   ├── static/              # Integrated Web UI & PWA Assets
│   │   │   ├── index.html       # Professor Portal (Classroom Scanner & Review Queue)
│   │   │   ├── student.html     # Student Portal (3-Angle Guided Camera Registration)
│   │   │   ├── sw.js            # PWA Service Worker for offline asset caching
│   │   │   ├── manifest.json    # PWA Web App Manifest
│   │   │   └── icons/           # App launcher icons (192x192, 512x512, apple-touch)
│   │   └── utils/
│   │       ├── image_utils.py   # OpenCV format conversion & face cropping
│   │       └── security.py      # Bcrypt password hashing & PyJWT token handling
│   └── requirements.txt         # Backend Python dependencies
├── docs/                        # Complete technical documentation suite
│   ├── API.md                   # REST API endpoint contracts & schemas
│   ├── ARCHITECTURE.md          # System architecture, dataflow & ML pipelines
│   ├── DEPLOYMENT.md            # Production deployment guide (Render, Docker, UptimeRobot)
│   ├── PRD.md                   # Product Requirements Document & specifications
│   ├── STRUCTURE.md             # Repository layout & module index
│   ├── UI_DESIGN.md             # UI/UX design system & token definitions
│   └── WORKFLOWS.md             # Step-by-step user journeys & edge cases
├── frontend/                    # Optional React + Vite SPA client
│   ├── src/                     # React application source code
│   ├── package.json             # Frontend npm dependencies
│   └── vite.config.js           # Vite build configuration
├── scripts/
│   ├── download_models.py       # Pre-downloads & caches InsightFace buffalo_sc models
│   └── phase1_prototype.py      # Standalone headless testing script
├── Dockerfile                   # Multi-stage production container image
├── docker-compose.yml           # Local & VPS container orchestration
├── render.yaml                  # 1-Click Render.com cloud deployment blueprint
├── requirements.txt             # Root Python dependencies for cloud build
├── LICENSE                      # MIT Open Source License
├── README.md                    # Main project overview & documentation
└── .gitignore                   # Excludes models, biometric photos & local databases
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
