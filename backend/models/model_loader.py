import json
import logging
from functools import lru_cache
from pathlib import Path

import numpy as np

from config import Config

LOGGER = logging.getLogger(__name__)

_MODEL = None
_TENSORFLOW_AVAILABLE = False

FALLBACK_LABELS = [
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___healthy",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Potato___Early_blight",
    "Potato___healthy",
    "Potato___Late_blight",
    "Tomato__Target_Spot",
    "Tomato__Tomato_mosaic_virus",
    "Tomato__Tomato_YellowLeaf__Curl_Virus",
    "Tomato_Bacterial_spot",
    "Tomato_Early_blight",
    "Tomato_healthy",
    "Tomato_Late_blight",
    "Tomato_Leaf_Mold",
    "Tomato_Septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite",
]


def _load_tensorflow_model():
    global _MODEL, _TENSORFLOW_AVAILABLE
    if _MODEL is not None:
        return _MODEL

    try:
        from tensorflow.keras.models import load_model  # type: ignore

        _TENSORFLOW_AVAILABLE = True
        if Config.MODEL_PATH.exists():
            _MODEL = load_model(Config.MODEL_PATH)
            LOGGER.info("Loaded TensorFlow model from %s", Config.MODEL_PATH)
        else:
            LOGGER.warning("Model file not found at %s.", Config.MODEL_PATH)
    except Exception as exc:  # pragma: no cover
        LOGGER.warning("TensorFlow model not loaded: %s.", exc)
        _MODEL = None
    return _MODEL


@lru_cache(maxsize=1)
def load_labels():
    if Config.LABELS_PATH.exists():
        with Config.LABELS_PATH.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # Support {"0":"classA", "1":"classB"} format
            return [value for _, value in sorted(data.items(), key=lambda item: int(item[0]))]

    return FALLBACK_LABELS.copy()


def _fallback_predict(image_batch: np.ndarray):
    labels = load_labels()
    image = image_batch[0]
    channel_means = image.mean(axis=(0, 1))
    red, green, blue = channel_means

    if green > red and green > blue:
        disease_key = "Tomato___healthy"
        confidence = 0.66
    elif red > green and red > blue:
        disease_key = "Tomato___Early_blight"
        confidence = 0.61
    else:
        disease_key = "Tomato___Late_blight"
        confidence = 0.58

    probs = np.full(len(labels), 0.01, dtype=np.float32)
    idx = labels.index(disease_key) if disease_key in labels else 0
    probs[idx] = confidence
    probs = probs / probs.sum()
    return probs


def _crop_from_label(label: str) -> str:
    normalized = label.lower()
    if "tomato" in normalized:
        return "tomato"
    if "potato" in normalized:
        return "potato"
    if "maize" in normalized or "corn" in normalized:
        return "maize"
    return "unknown"


def _load_training_summary():
    path = Path(Config.TRAINING_SUMMARY_PATH)
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as fp:
            return json.load(fp)
    except Exception:  # pragma: no cover
        return {}


def predict_probabilities(image_batch: np.ndarray):
    model = _load_tensorflow_model()
    labels = load_labels()

    if model is None:
        if not Config.ALLOW_FALLBACK_MODEL:
            raise RuntimeError(
                "Trained model is not loaded. Install backend dependencies and ensure "
                f"model exists at {Config.MODEL_PATH}."
            )
        probs = _fallback_predict(image_batch)
    else:
        model_output = model.predict(image_batch, verbose=0)[0]
        probs = np.array(model_output, dtype=np.float32)

    if probs.shape[0] != len(labels):
        raise ValueError(
            f"Model output length ({probs.shape[0]}) does not match labels length ({len(labels)})."
        )

    return probs, labels


def model_status():
    model = _load_tensorflow_model()
    labels = load_labels()
    supported_crops = sorted({crop for crop in (_crop_from_label(label) for label in labels) if crop != "unknown"})
    summary = _load_training_summary()
    return {
        "using_trained_model": model is not None,
        "tensorflow_available": _TENSORFLOW_AVAILABLE,
        "allow_fallback_model": Config.ALLOW_FALLBACK_MODEL,
        "model_path": str(Config.MODEL_PATH),
        "labels_path": str(Config.LABELS_PATH),
        "labels_count": len(labels),
        "supported_crops": supported_crops,
        "training_data_dir": summary.get("data_dir"),
        "training_dataset_source": summary.get("dataset_source"),
        "training_total_images": summary.get("total_images"),
        "training_class_count": summary.get("class_count"),
    }
