import zipfile
import json
import os

def load_model_pack(path):

    with zipfile.ZipFile(path, 'r') as zip_ref:
        extract_path = "model_packs/extracted/"
        zip_ref.extractall(extract_path)

    with open(os.path.join(extract_path, "config.json")) as f:
        config = json.load(f)

    return extract_path, config