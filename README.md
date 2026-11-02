# FaceMark (FRCAS) - Face Recognition Classroom Attendance System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg)](https://fastapi.tiangolo.com/)
[![InsightFace](https://img.shields.io/badge/AI%20Engine-RetinaFace%20%2B%20ArcFace-indigo.svg)](https://github.com/deepinsight/insightface)
[![PWA Ready](https://img.shields.io/badge/PWA-Installable-purple.svg)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
[![Compliance](https://img.shields.io/badge/DPDP%20Act%202023-Compliant-emerald.svg)](https://www.meity.gov.in/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Enterprise-grade classroom attendance automation engineered with **RetinaFace (detection)**, **ArcFace 512-D (biometric vectors)**, **FastAPI**, and an installable **Progressive Web App (PWA)** interface. Take attendance for 60+ students in under 45 seconds with zero manual roll calling and zero proxy attendance.

---

## Key Highlights

1. **Dual-Threshold AI Safety Net**:
   * **>= 0.60 Cosine Similarity:** Auto-marked Present (Green, >99.5% confidence).
   * **0.40 - 0.59 Similarity:** Sent to Teacher Review Queue (Amber) with side-by-side face comparison.
   * **< 0.40 Similarity:** Unknown / Visitor (Blue dashed).
2. **Unlimited Classroom Sector Snapping**:
   * Lecturers can snap as many room angles as needed (Front Rows, Back Benches, Left Wing, Center, Right Wing, Corner Seats).
   * Bipartite matching with greedy assignment resolves overlapping photos to the single highest-confidence detection per student with zero duplicate records.
3. **Manual Attendance Override & Quick Add**:
   * One-click **Add to Attendance Sheet** button for any student marked absent.
   * Dedicated toolbar to quickly mark enrolled students or register walk-in students on the spot.
4. **Studio 3-Angle Face Scanner (Zero Photo Uploads)**:
   * Interactive camera enrollment guiding students through 3 poses: **Center (0 deg)**, **Left (~20 deg)**, and **Right (~20 deg)** with live audio-visual feedback.
5. **College-Ready Multi-Sheet Excel Reports**:
   * **Sheet 1 (Session Attendance):** Formatted session records with verification method (AI Facial Recognition vs. Teacher Manual Override).
   * **Sheet 2 (Cumulative Summary):** Semester-to-date attendance metrics, overall percentage, and automatic eligibility shortage warnings highlighted in soft red for students below 75%.
6. **Progressive Web App (PWA)**:
   * Installable on Windows, macOS, Android, and iOS. Operates in standalone window without browser address bars.
7. **India DPDP Act 2023 Compliance**:
   * Plain-language biometric consent recording, vector-only storage, and permanent data deletion support (Right to be Forgotten).

---

## Two Dedicated Web Portals

| Portal | URL | Description | Default Login |
|---|---|---|---|
| **Professor Portal** | `http://localhost:8000` or `/professor` | Executive dashboard, unlimited room scanner, dual-panel review canvas, student roster, class manager, and Excel reports. | `teacher@college.edu` / `admin123` |
| **Student Scanner** | `http://localhost:8000/student` | Public guided 3-pose camera face enrollment scanner for smartphones and lab computers. | Self-Registration (No login needed) |

---

## Detailed Documentation (`docs/`)

Explore the technical specifications and architecture docs:

* [**Product Requirements Document (PRD)**](docs/PRD.md) - Functional and technical specifications, acceptance criteria, and edge cases.
* [**Production Deployment Guide**](docs/DEPLOYMENT.md) - Cloud (Render/Railway), Campus LAN, and Docker VPS setup.
* [**System Architecture**](docs/ARCHITECTURE.md) - Pipeline dataflow, bipartite matching, model ONNX runtimes, and database schema.
* [**UI/UX Design Specification**](docs/UI_DESIGN.md) - Design tokens, color calibration, dual-portal flows, and keyboard accessibility.
* [**REST API Documentation**](docs/API.md) - Endpoint reference, request/response payloads, and authentication guides.
* [**Directory Structure**](docs/STRUCTURE.md) - Monorepo tree breakdown and module ownership.
* [**User Workflows**](docs/WORKFLOWS.md) - Step-by-step user journeys for lecturers and students.

---

## Quickstart Guide

### 1. Prerequisites
* Python 3.10+
* Web browser with camera permissions (Chrome, Edge, Safari, Brave)

### 2. Setup & Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/PavanCodeNexus/FRCAS.git
cd FRCAS
pip install -r requirements.txt
```

### 3. Launch the Server

Run Uvicorn from the project root:

```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at:
**[http://localhost:8000](http://localhost:8000)**

* **Teacher Demo Login:** `teacher@college.edu` / `admin123`
* **Student Self-Enrollment:** `http://localhost:8000/student`

---

## Installing as a PWA

1. **Desktop (Chrome / Edge):** Click the **Install App** button in the top navbar or the install icon in your browser address bar.
2. **Android:** Tap the **Install App** button or select `Add to Home screen` from the Chrome menu.
3. **iOS (Safari):** Tap **Share -> Add to Home Screen**.

---

## Repository Structure

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

---

## Privacy & Compliance

FaceMark is built strictly adhering to **India Digital Personal Data Protection (DPDP) Act 2023**:
* Raw facial images can be purged after embedding extraction.
* Face features are stored as one-way 512-dimensional float vectors that cannot be reconstructed back into original faces.
* Students can invoke their Right to Erasure at any time through the Student Roster portal.

---

## License

This project is open-source under the [MIT License](LICENSE).
