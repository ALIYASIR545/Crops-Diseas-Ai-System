from datetime import datetime, timezone

from flask import Blueprint, jsonify

from models.model_loader import model_status

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health_check():
    return jsonify(
        {
            "status": "ok",
            "service": "smart-crop-disease-backend",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "model": model_status(),
        }
    )
