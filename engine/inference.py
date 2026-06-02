import onnxruntime as ort
import numpy as np

class U2NetRunner:

    def __init__(self, model_path):
        self.session = ort.InferenceSession(model_path)

    def predict(self, input_tensor):
        outputs = self.session.run(
            None,
            {"input": input_tensor}
        )

        return outputs[0]