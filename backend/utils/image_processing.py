import numpy as np
from PIL import Image


def load_and_preprocess_image(image_path: str, target_size=(224, 224)) -> np.ndarray:
    image = Image.open(image_path).convert("RGB")
    image = image.resize(target_size)
    image_arr = np.asarray(image, dtype=np.float32) / 255.0
    return np.expand_dims(image_arr, axis=0)
