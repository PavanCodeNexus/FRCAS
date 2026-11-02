import cv2
import numpy as np
import base64
from PIL import Image, ImageOps
import io
from typing import Tuple, Optional, List

def bytes_to_cv2_image(image_bytes: bytes) -> np.ndarray:
    """Reads image bytes, corrects EXIF orientation (crucial for phone photos), and returns BGR cv2 image."""
    pil_image = Image.open(io.BytesIO(image_bytes))
    pil_image = ImageOps.exif_transpose(pil_image)
    if pil_image.mode != "RGB":
        pil_image = pil_image.convert("RGB")
    rgb_arr = np.array(pil_image)
    bgr_arr = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2BGR)
    return bgr_arr

def crop_face(image: np.ndarray, bbox: List[int], margin_ratio: float = 0.2) -> np.ndarray:
    """Crops a face from an image with an optional margin around bounding box [x1, y1, x2, y2]."""
    h, w = image.shape[:2]
    x1, y1, x2, y2 = bbox
    box_w = x2 - x1
    box_h = y2 - y1

    pad_w = int(box_w * margin_ratio)
    pad_h = int(box_h * margin_ratio)

    cx1 = max(0, x1 - pad_w)
    cy1 = max(0, y1 - pad_h)
    cx2 = min(w, x2 + pad_w)
    cy2 = min(h, y2 + pad_h)

    crop = image[cy1:cy2, cx1:cx2]
    return crop

def cv2_to_base64_jpeg(image: np.ndarray, quality: int = 85) -> str:
    """Encodes a BGR image array into a base64 JPEG string for easy frontend rendering."""
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    success, buffer = cv2.imencode('.jpg', image, encode_params)
    if not success:
        return ""
    b64_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{b64_str}"

def resize_if_needed(image: np.ndarray, max_dimension: int = 2560) -> np.ndarray:
    """Resizes very large photos (e.g., 48MP) to reasonable processing bounds while maintaining aspect ratio."""
    h, w = image.shape[:2]
    if max(h, w) <= max_dimension:
        return image
    scale = max_dimension / float(max(h, w))
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
