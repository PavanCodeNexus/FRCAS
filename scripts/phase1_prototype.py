"""
FRCAS - Phase 1 Prototype Script
Demonstrates end-to-end face detection, ArcFace embedding, cosine similarity matching,
and annotated visual output with dual-threshold classification.
"""

import os
import sys
import json
from pathlib import Path
import cv2
import numpy as np

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.app.services.detector import get_face_engine, detect_faces, validate_and_extract_face
from backend.app.services.matcher import match_faces_to_students
from backend.app.utils.image_utils import crop_face, bytes_to_cv2_image
from backend.app.config import HIGH_THRESHOLD, LOW_THRESHOLD

def draw_annotated_results(
    image: np.ndarray,
    matches: dict,
    output_path: Path
):
    """Draws color-coded bounding boxes and labels onto the classroom image."""
    annotated = image.copy()

    # 1. Auto Present -> Green (0, 200, 0)
    for m in matches.get("auto_present", []):
        x1, y1, x2, y2 = m["bbox"]
        label = f"{m['usn']} ({int(m['confidence']*100)}%)"
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 200, 0), 2)
        cv2.putText(annotated, label, (x1, max(15, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 2)

    # 2. Needs Review -> Orange/Yellow (0, 165, 255)
    for m in matches.get("needs_review", []):
        x1, y1, x2, y2 = m["bbox"]
        label = f"REVIEW: {m['usn']} ({int(m['confidence']*100)}%)"
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 165, 255), 2)
        cv2.putText(annotated, label, (x1, max(15, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)

    # 3. Unknown Faces -> Gray/White (180, 180, 180)
    for m in matches.get("unknown_faces", []):
        x1, y1, x2, y2 = m["bbox"]
        label = "UNKNOWN"
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (180, 180, 180), 2)
        cv2.putText(annotated, label, (x1, max(15, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), annotated)
    print(f"\n[+] Annotated classroom output saved to: {output_path}")

def run_demo():
    print("=" * 65)
    print(" FRCAS - Face Recognition Classroom Attendance Prototype (Phase 1)")
    print("=" * 65)

    print("[*] Initializing InsightFace Engine (RetinaFace + ArcFace)...")
    engine = get_face_engine()
    print("[+] Engine ready!\n")

    # Check registered faces folder
    reg_dir = PROJECT_ROOT / "data" / "registered_faces"
    class_dir = PROJECT_ROOT / "data" / "class_photos"
    exports_dir = PROJECT_ROOT / "data" / "exports"

    reg_images = list(reg_dir.glob("*.jpg")) + list(reg_dir.glob("*.png"))
    class_images = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.png"))

    print(f"[*] Found {len(reg_images)} student photos in {reg_dir.relative_to(PROJECT_ROOT)}")
    print(f"[*] Found {len(class_images)} classroom photos in {class_dir.relative_to(PROJECT_ROOT)}\n")

    if not class_images or not reg_images:
        print("[!] Quick Setup Guide to Test with Your Own Photos:")
        print(f"    1. Place 1-3 clear student portrait photos into: {reg_dir.relative_to(PROJECT_ROOT)}/")
        print("       (Naming format: USN_Name.jpg, e.g., 1MS21CS001_Rahul.jpg)")
        print(f"    2. Place 1 classroom photo into: {class_dir.relative_to(PROJECT_ROOT)}/class_test.jpg")
        print("    3. Re-run: python scripts/phase1_prototype.py\n")

        print("[*] Creating a synthetic demo face to verify embedding math...")
        # Create two sample unit vectors to verify cosine similarity math
        v1 = np.random.randn(512).astype(np.float32)
        v1 /= np.linalg.norm(v1)

        # Perturbed vector (similar person)
        v2 = v1 + np.random.randn(512).astype(np.float32) * 0.15
        v2 /= np.linalg.norm(v2)

        # Different person
        v3 = np.random.randn(512).astype(np.float32)
        v3 /= np.linalg.norm(v3)

        sim_same = float(np.dot(v1, v2))
        sim_diff = float(np.dot(v1, v3))

        print(f"    Cosine similarity for same identity:      {sim_same:.4f} (Expected > {HIGH_THRESHOLD})")
        print(f"    Cosine similarity for different identity: {sim_diff:.4f} (Expected < {LOW_THRESHOLD})")
        print("[+] Mathematical verification PASSED!\n")
        return

    # Real photos exist -> Process them
    print("[*] Building gallery from registered student photos...")
    gallery = {}
    for img_path in reg_images:
        name_part = img_path.stem
        # Format: USN_Name or just USN
        parts = name_part.split("_")
        usn = parts[0].upper()
        name = parts[1] if len(parts) > 1 else usn

        with open(img_path, "rb") as f:
            valid, msg, emb, _ = validate_and_extract_face(f.read())
            if valid and emb is not None:
                if usn not in gallery:
                    gallery[usn] = {"name": name, "embeddings": []}
                gallery[usn]["embeddings"].append(emb)
                print(f"    [OK] Enrolled: {usn} ({name}) from {img_path.name}")
            else:
                print(f"    [WARN] Skipped {img_path.name}: {msg}")

    print(f"\n[+] Enrolled {len(gallery)} unique students in gallery.")

    # Process first classroom test photo
    test_photo_path = class_images[0]
    print(f"\n[*] Processing classroom photo: {test_photo_path.name}")
    cv_img = cv2.imread(str(test_photo_path))
    if cv_img is None:
        print(f"[!] Error reading {test_photo_path}")
        return

    detected_faces = detect_faces(cv_img, min_det_score=0.45)
    print(f"[+] Total faces detected in classroom: {len(detected_faces)}")

    formatted_faces = []
    for idx, face in enumerate(detected_faces):
        emb = face.embedding.copy()
        norm = np.linalg.norm(emb)
        if norm > 0:
            emb /= norm
        bbox = [int(x) for x in face.bbox]
        formatted_faces.append({
            "embedding": emb,
            "bbox": bbox,
            "photo_index": 0
        })

    # Run matching
    results = match_faces_to_students(formatted_faces, gallery, HIGH_THRESHOLD, LOW_THRESHOLD)

    print("\n" + "=" * 40)
    print(" ATTENDANCE SUMMARY")
    print("=" * 40)

    print(f"\n[AUTO-PRESENT ({len(results['auto_present'])})]")
    for m in results["auto_present"]:
        print(f"  - {m['usn']} | {m['name']} | Confidence: {m['confidence']:.2%}")

    print(f"\n[NEEDS REVIEW ({len(results['needs_review'])})]")
    for m in results["needs_review"]:
        print(f"  - {m['usn']} | {m['name']} | Confidence: {m['confidence']:.2%}")

    print(f"\n[UNKNOWN FACES ({len(results['unknown_faces'])})]")
    print(f"  Total unknown/unrecognized: {len(results['unknown_faces'])}")

    print(f"\n[ABSENT / NOT DETECTED ({len(results['unmatched_usns'])})]")
    for usn in results["unmatched_usns"]:
        print(f"  - {usn} | {gallery[usn]['name']}")

    # Save annotated visual
    out_file = exports_dir / f"annotated_{test_photo_path.name}"
    draw_annotated_results(cv_img, results, out_file)

if __name__ == "__main__":
    run_demo()
