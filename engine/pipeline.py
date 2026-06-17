
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ProgressUpdate:
    stage: str
    label: str
    percent: int | None
    busy: bool = False


def build_output_path(image_path):
    base, _ = os.path.splitext(image_path)
    return f"{base}_nobg.png"


def _report(progress_callback, update):
    if progress_callback:
        progress_callback(update)


def remove_background(image_path, progress_callback=None):
    """Remove background using rembg and save PNG with alpha channel.

    Returns the output file path.
    """
    from PIL import Image
    from rembg import remove

    _report(
        progress_callback,
        ProgressUpdate("loading", "Loading source image", 12),
    )
    img = Image.open(image_path)

    _report(
        progress_callback,
        ProgressUpdate("removing", "Removing background", None, busy=True),
    )
    result = remove(img, 
                    alpha_matting_foreground_threshold=270, 
                    alpha_matting_background_threshold=15)

    outpath = build_output_path(image_path)

    _report(
        progress_callback,
        ProgressUpdate("saving", "Saving transparent PNG", 88),
    )
    # `result` is a PIL Image with transparency; save as PNG
    result.save(outpath)

    _report(
        progress_callback,
        ProgressUpdate("done", "Done", 100),
    )
    return outpath
