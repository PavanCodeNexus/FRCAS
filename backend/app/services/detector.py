import os
from typing import List, Tuple, Optional, Any
import numpy as np
import cv2
import onnxruntime
from insightface.app import FaceAnalysis
from ..config import BASE_DIR, INSIGHTFACE_MODEL, DET_CONF_THRESHOLD
from ..utils.image_utils import bytes_to_cv2_image, crop_face

_face_app: Optional[FaceAnalysis] = None

def get_face_engine() -> FaceAnalysis:
    """Singleton getter for InsightFace engine."""
    global _face_app
    if _face_app is None:
        models_root = str(BASE_DIR / "models")
        available = onnxruntime.get_available_providers()
        providers = [p for p in ['CUDAExecutionProvider', 'CPUExecutionProvider'] if p in available]
        if not providers:
            providers = ['CPUExecutionProvider']
        _face_app = FaceAnalysis(name=INSIGHTFACE_MODEL, root=models_root, providers=providers)
        # Use detection size 640x640 for high accuracy
        _face_app.prepare(ctx_id=0, det_size=(640, 640))
    return _face_app

def detect_faces(image: np.ndarray, min_det_score: float = DET_CONF_THRESHOLD) -> List[Any]:
    """Detects all faces in an image and filters by minimum detection score."""
    engine = get_face_engine()
    raw_faces = engine.get(image)
    valid_faces = [f for f in raw_faces if f.det_score >= min_det_score]
    return valid_faces

def validate_and_extract_face(image_bytes: bytes) -> Tuple[bool, str, Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Validates a student registration photo:
    - Must contain exactly 1 face.
    - Returns (is_valid, message, normalized_embedding, face_crop)
    """
    try:
        cv_img = bytes_to_cv2_image(image_bytes)
    except Exception as e:
        return False, f"Failed to read image file: {str(e)}", None, None

    faces = detect_faces(cv_img, min_det_score=0.55)

    if len(faces) == 0:
        return False, "No face detected in photo. Ensure lighting is clear and look towards the camera.", None, None
    elif len(faces) > 1:
        return False, f"Multiple faces ({len(faces)}) detected. Registration photo must only show one student.", None, None

    face = faces[0]
    embedding = face.embedding.copy()
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm

    # Extract clean face crop
    bbox = [int(x) for x in face.bbox]
    face_crop = crop_face(cv_img, bbox, margin_ratio=0.25)

    return True, "Valid face registered", embedding, face_crop
