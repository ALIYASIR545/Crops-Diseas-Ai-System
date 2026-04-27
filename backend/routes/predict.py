import uuid
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from config import Config
from utils.db import insert_prediction
from utils.prediction import (
    PredictionError,
    build_localized_response,
    infer_crop_from_disease_key,
    predict_disease_from_image,
)
from utils.weather import get_weather_risk

predict_bp = Blueprint("predict", __name__)
ALLOWED_CROPS = {"tomato", "potato", "maize", "corn"}


def _safe_filename(filename: str) -> str:
    suffix = Path(filename or "leaf.jpg").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"
    return f"{uuid.uuid4().hex}{suffix}"


@predict_bp.post("/predict")
def predict():
    if "image" not in request.files:
        return jsonify({"error": "Image file is required (multipart form-data key: image)."}), 400

    image = request.files["image"]
    if not image or image.filename == "":
        return jsonify({"error": "Image filename is missing."}), 400

    farmer_id = request.form.get("farmer_id", "anonymous").strip() or "anonymous"
    crop = request.form.get("crop", "").strip()
    lang = request.form.get("lang", "en").strip().lower()
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")

    normalized_crop = crop.lower()
    if normalized_crop and normalized_crop not in ALLOWED_CROPS:
        return jsonify({"error": "Supported crops are Tomato, Potato, and Maize."}), 400
    if normalized_crop == "corn":
        normalized_crop = "maize"

    filename = _safe_filename(image.filename)
    upload_path = current_app.config["UPLOAD_DIR"] / filename
    image.save(upload_path)

    try:
        prediction = predict_disease_from_image(str(upload_path))
    except PredictionError as exc:
        return jsonify({"error": str(exc)}), 500

    weather = get_weather_risk(latitude=latitude, longitude=longitude, disease_key=prediction["disease_key"])
    response_payload = build_localized_response(prediction, lang=lang)
    response_payload["weather_risk"] = weather
    predicted_crop = infer_crop_from_disease_key(prediction["disease_key"])

    response_payload["meta"] = {
        "farmer_id": farmer_id,
        "requested_crop": normalized_crop or "",
        "predicted_crop": predicted_crop,
        "image_filename": filename,
    }
    if normalized_crop and predicted_crop != "unknown" and normalized_crop != predicted_crop:
        response_payload["warning"] = (
            f"Uploaded crop '{normalized_crop}' differs from detected crop '{predicted_crop}'. "
            "Please verify the image and crop selection."
        )

    record_id = insert_prediction(
        db_path=Config.DATABASE_PATH,
        farmer_id=farmer_id,
        crop=normalized_crop or crop,
        image_path=str(upload_path),
        disease_key=prediction["disease_key"],
        confidence=prediction["confidence"],
        weather_risk=weather.get("risk_level", "unknown"),
    )
    response_payload["history_id"] = record_id
    return jsonify(response_payload)
