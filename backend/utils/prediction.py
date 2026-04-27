import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import numpy as np

from config import Config
from models.model_loader import predict_probabilities
from utils.image_processing import load_and_preprocess_image


class PredictionError(Exception):
    pass


def _normalize_key(label: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", label.strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized


def infer_crop_from_disease_key(disease_key: str) -> str:
    normalized = _normalize_key(disease_key)
    if "tomato" in normalized:
        return "tomato"
    if "potato" in normalized:
        return "potato"
    if "maize" in normalized or "corn" in normalized:
        return "maize"
    return "unknown"


@lru_cache(maxsize=1)
def _load_recommendations() -> Dict[str, Dict[str, Any]]:
    if not Config.RECOMMENDATIONS_PATH.exists():
        raise PredictionError(
            f"Recommendation file not found: {Config.RECOMMENDATIONS_PATH}. "
            "Create backend/data/disease_recommendations.json first."
        )
    with Config.RECOMMENDATIONS_PATH.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def get_recommendation_for_key(disease_key: str) -> Dict[str, Any]:
    data = _load_recommendations()
    key = _normalize_key(disease_key)
    if key in data:
        return data[key]

    for candidate_key in data.keys():
        if _normalize_key(candidate_key).lower() == key.lower():
            return data[candidate_key]

    return data.get("Unknown", data[next(iter(data))])


def predict_disease_from_image(image_path: str) -> Dict[str, Any]:
    if not Path(image_path).exists():
        raise PredictionError("Uploaded image file could not be found on server.")

    try:
        batch = load_and_preprocess_image(image_path=image_path)
        probs, labels = predict_probabilities(batch)
    except Exception as exc:
        raise PredictionError(f"Prediction failed: {exc}") from exc

    top_idx = int(np.argmax(probs))
    top_conf = float(probs[top_idx])
    disease_key = labels[top_idx]

    top3_indices = np.argsort(probs)[::-1][:3]
    top3 = [
        {
            "disease_key": labels[int(i)],
            "confidence": round(float(probs[int(i)]), 4),
        }
        for i in top3_indices
    ]

    recommendation = get_recommendation_for_key(disease_key)
    return {
        "disease_key": disease_key,
        "confidence": round(top_conf, 4),
        "top_predictions": top3,
        "recommendation": recommendation,
    }


def build_localized_response(prediction: Dict[str, Any], lang: str = "en") -> Dict[str, Any]:
    language = "ur" if lang == "ur" else "en"
    rec = prediction["recommendation"]

    return {
        "disease_key": prediction["disease_key"],
        "disease_name": rec["disease_name"].get(language, rec["disease_name"]["en"]),
        "crop_name": rec["crop_name"].get(language, rec["crop_name"]["en"]),
        "confidence": prediction["confidence"],
        "top_predictions": prediction["top_predictions"],
        "recommendation": {
            "pesticide": rec["pesticide"].get(language, rec["pesticide"]["en"]),
            "dosage": rec["dosage"].get(language, rec["dosage"]["en"]),
            "treatment_steps": rec["treatment_steps"].get(language, rec["treatment_steps"]["en"]),
            "prevention_tips": rec["prevention_tips"].get(language, rec["prevention_tips"]["en"]),
        },
    }
