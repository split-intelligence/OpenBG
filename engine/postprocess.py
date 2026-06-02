import cv2
import numpy as np

def postprocess_mask(mask, original_shape):

    mask = mask.squeeze()

    mask = cv2.resize(
        mask,
        (original_shape[1], original_shape[0]),
        interpolation=cv2.INTER_LINEAR
    )

    mask = (mask - mask.min()) / (mask.max() - mask.min() + 1e-8)

    mask = (mask * 255).astype(np.uint8)

    # edge refinement
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    return mask