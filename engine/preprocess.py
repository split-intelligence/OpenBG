import cv2
import numpy as np

def preprocess_image(path):
    image = cv2.imread(path)
    original = image.copy()

    image = cv2.resize(image, (320, 320))
    image = image.astype(np.float32) / 255.0

    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])

    image = (image - mean) / std
    image = image.transpose(2, 0, 1)
    image = np.expand_dims(image, axis=0)

    return image, original