import cv2
import numpy as np
import os

def save_png(image, mask, original_path):

    b, g, r = cv2.split(image)

    rgba = cv2.merge([b, g, r, mask])

    output_path = original_path.replace(".jpg", "_nobg.png")

    cv2.imwrite(output_path, rgba)

    return output_path