import onnxruntime as ort
import numpy as np

class U2NetRunner:

    def __init__(self, model_path):
        self.session = ort.InferenceSession(model_path)
        # determine the correct input name from the model
        inputs = self.session.get_inputs()
        if not inputs:
            raise RuntimeError("ONNX model has no inputs")
        self.input_name = inputs[0].name

    def predict(self, input_tensor):
        # ensure input is a numpy array of dtype float32 and contiguous
        input_array = np.asarray(input_tensor, dtype=np.float32)
        input_array = np.ascontiguousarray(input_array)

        # use the model's actual input name to avoid 'required inputs missing' errors
        outputs = self.session.run(None, {self.input_name: input_array})
        return outputs[0]