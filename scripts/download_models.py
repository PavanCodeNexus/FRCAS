"""
Helper script to pre-download and cache InsightFace models for production deployment.
Runs during Docker build or system initialization.
"""
import os
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import onnxruntime
from insightface.app import FaceAnalysis

def download_models(model_name="buffalo_sc", root_dir=None):
    if root_dir is None:
        root_dir = str(BASE_DIR / "models")
    
    print(f"[*] Pre-downloading InsightFace model '{model_name}' to: {root_dir}")
    os.makedirs(root_dir, exist_ok=True)
    
    available = onnxruntime.get_available_providers()
    providers = [p for p in ['CUDAExecutionProvider', 'CPUExecutionProvider'] if p in available]
    if not providers:
        providers = ['CPUExecutionProvider']
        
    app = FaceAnalysis(name=model_name, root=root_dir, providers=providers)
    app.prepare(ctx_id=0, det_size=(640, 640))
    print(f"[✓] Model '{model_name}' successfully cached and ready for inference!")

if __name__ == "__main__":
    target = os.getenv("INSIGHTFACE_MODEL", "buffalo_sc")
    download_models(target)
