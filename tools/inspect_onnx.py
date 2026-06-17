import onnxruntime as ort

sess = ort.InferenceSession('models/u2net.onnx')
inputs = sess.get_inputs()
print('INPUT_NAMES:', [i.name for i in inputs])
print('INPUT_SHAPES:', [i.shape for i in inputs])
print('INPUT_TYPES:', [i.type for i in inputs])
