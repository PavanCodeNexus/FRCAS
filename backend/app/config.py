import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
REGISTERED_FACES_DIR = DATA_DIR / "registered_faces"
CLASS_PHOTOS_DIR = DATA_DIR / "class_photos"
EXPORTS_DIR = DATA_DIR / "exports"

for d in [DATA_DIR, REGISTERED_FACES_DIR, CLASS_PHOTOS_DIR, EXPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/face_attendance.db")

# Security / JWT
SECRET_KEY = os.getenv("SECRET_KEY", "frcas-super-secret-key-change-in-production-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Recognition Thresholds
HIGH_THRESHOLD = float(os.getenv("HIGH_THRESHOLD", "0.60"))  # Auto-mark PRESENT
LOW_THRESHOLD = float(os.getenv("LOW_THRESHOLD", "0.40"))    # Send to REVIEW queue
DET_CONF_THRESHOLD = float(os.getenv("DET_CONF_THRESHOLD", "0.50"))

# InsightFace configuration
INSIGHTFACE_MODEL = os.getenv("INSIGHTFACE_MODEL", "buffalo_l")
