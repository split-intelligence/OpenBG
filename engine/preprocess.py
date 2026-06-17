import cv2
import numpy as np

def preprocess_image(path):
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError(f"Could not load image: {path}")
    original = image.copy()

    image = cv2.resize(image, (320, 320))
    # force float32 before any arithmetic to avoid accidental upcasting to float64
    image = image.astype(np.float32)
    image /= np.float32(255.0)

    # use float32 means/std to avoid upcasting the image to float64
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    image = (image - mean) / std
    # ensure final tensor is contiguous float32 (ONNXRuntime expects float32)
    image = np.ascontiguousarray(image, dtype=np.float32)
    image = image.transpose(2, 0, 1)
    image = np.expand_dims(image, axis=0)

    return image, original