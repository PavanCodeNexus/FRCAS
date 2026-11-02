from typing import List, Optional, Any
import numpy as np
from .detector import get_face_engine

def extract_normalized_embedding(face_obj: Any) -> np.ndarray:
    """Extracts and L2-normalizes the 512-D ArcFace embedding from an InsightFace face object."""
    emb = face_obj.embedding.copy()
    norm = np.linalg.norm(emb)
    if norm > 0:
        emb = emb / norm
    return emb

def generate_embedding_from_crop(face_crop_bgr: np.ndarray) -> Optional[np.ndarray]:
    """Generates embedding directly from a cropped face image."""
    engine = get_face_engine()
    faces = engine.get(face_crop_bgr)
    if not faces:
        return None
    return extract_normalized_embedding(faces[0])
