import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from ..config import HIGH_THRESHOLD, LOW_THRESHOLD

def compute_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Computes cosine similarity between two normalized vectors."""
    dot = np.dot(vec1, vec2)
    return float(np.clip(dot, -1.0, 1.0))

def match_faces_to_students(
    detected_faces: List[Dict[str, Any]],
    student_gallery: Dict[str, Dict[str, Any]],
    high_threshold: float = HIGH_THRESHOLD,
    low_threshold: float = LOW_THRESHOLD
) -> Dict[str, Any]:
    """
    Matches detected faces against a section's registered student gallery.

    Arguments:
    - detected_faces: List of dicts with keys:
        'embedding' (np.ndarray 512-D),
        'bbox' ([x1, y1, x2, y2]),
        'photo_index' (int),
        'crop_b64' (str)
    - student_gallery: Dict mapping USN to:
        {'name': str, 'embeddings': List[np.ndarray]}
    - high_threshold: similarity threshold for AUTO_PRESENT
    - low_threshold: similarity threshold for NEEDS_REVIEW

    Returns:
    - dict with:
        'auto_present': List[Dict]
        'needs_review': List[Dict]
        'unknown_faces': List[Dict]
        'unmatched_usns': List[str]
    """
    if not detected_faces:
        return {
            "auto_present": [],
            "needs_review": [],
            "unknown_faces": [],
            "unmatched_usns": list(student_gallery.keys())
        }

    usn_list = list(student_gallery.keys())
    if not usn_list:
        # No students registered in this section yet
        return {
            "auto_present": [],
            "needs_review": [],
            "unknown_faces": [
                {
                    "confidence": 0.0,
                    "bbox": f["bbox"],
                    "photo_index": f["photo_index"],
                    "face_crop_base64": f.get("crop_b64")
                }
                for f in detected_faces
            ],
            "unmatched_usns": []
        }

    # Build student similarity matrix: (num_faces, num_students)
    num_faces = len(detected_faces)
    num_students = len(usn_list)
    sim_matrix = np.zeros((num_faces, num_students), dtype=np.float32)

    for i, face in enumerate(detected_faces):
        f_emb = face["embedding"]
        for j, usn in enumerate(usn_list):
            student_embs = student_gallery[usn]["embeddings"]
            # Maximum similarity across all enrolled photo angles for this student
            best_sim = max(
                (float(np.dot(f_emb, s_emb)) for s_emb in student_embs),
                default=0.0
            )
            sim_matrix[i, j] = best_sim

    # Greedy highest-confidence bipartite matching to guarantee 1 USN is assigned to 1 face max
    assigned_faces = set()
    assigned_usns = set()

    # Create candidate pairs sorted by similarity descending
    candidate_pairs = []
    for i in range(num_faces):
        for j in range(num_students):
            candidate_pairs.append((sim_matrix[i, j], i, j))
    candidate_pairs.sort(key=lambda x: x[0], reverse=True)

    auto_present = []
    needs_review = []
    student_to_face_match = {}

    for sim, face_idx, student_idx in candidate_pairs:
        if face_idx in assigned_faces:
            continue
        usn = usn_list[student_idx]
        if usn in assigned_usns:
            continue

        if sim >= high_threshold:
            assigned_faces.add(face_idx)
            assigned_usns.add(usn)
            f_data = detected_faces[face_idx]
            match_data = {
                "usn": usn,
                "name": student_gallery[usn]["name"],
                "confidence": round(float(sim), 4),
                "bbox": f_data["bbox"],
                "photo_index": f_data["photo_index"],
                "face_crop_base64": f_data.get("crop_b64")
            }
            auto_present.append(match_data)
            student_to_face_match[usn] = match_data

        elif sim >= low_threshold:
            assigned_faces.add(face_idx)
            assigned_usns.add(usn)
            f_data = detected_faces[face_idx]
            match_data = {
                "usn": usn,
                "name": student_gallery[usn]["name"],
                "confidence": round(float(sim), 4),
                "bbox": f_data["bbox"],
                "photo_index": f_data["photo_index"],
                "face_crop_base64": f_data.get("crop_b64")
            }
            needs_review.append(match_data)
            student_to_face_match[usn] = match_data

    # Unassigned faces become "unknown"
    unknown_faces = []
    for i, face in enumerate(detected_faces):
        if i not in assigned_faces:
            # Find best candidate even if low score for review info
            best_idx = int(np.argmax(sim_matrix[i])) if num_students > 0 else 0
            best_score = float(sim_matrix[i, best_idx]) if num_students > 0 else 0.0
            unknown_faces.append({
                "usn": usn_list[best_idx] if best_score > 0.25 else None,
                "name": student_gallery[usn_list[best_idx]]["name"] if best_score > 0.25 else None,
                "confidence": round(best_score, 4),
                "bbox": face["bbox"],
                "photo_index": face["photo_index"],
                "face_crop_base64": face.get("crop_b64")
            })

    # Students who were not matched to any face
    unmatched_usns = [usn for usn in usn_list if usn not in assigned_usns]

    return {
        "auto_present": auto_present,
        "needs_review": needs_review,
        "unknown_faces": unknown_faces,
        "unmatched_usns": unmatched_usns
    }
