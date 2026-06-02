from engine.preprocess import preprocess_image
from engine.postprocess import postprocess_mask
from engine.inference import U2NetRunner
from export.png_export import save_png

runner = U2NetRunner("models/u2net.onnx")

def remove_background(image_path):

    image, original = preprocess_image(image_path)

    mask = runner.predict(image)

    refined_mask = postprocess_mask(mask, original.shape)

    output_path = save_png(original, refined_mask, image_path)

    return output_path