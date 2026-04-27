from flask import Blueprint, jsonify, request

from config import Config
from utils.db import fetch_history
from utils.prediction import get_recommendation_for_key

history_bp = Blueprint("history", __name__)


@history_bp.get("/history")
def history():
    farmer_id = request.args.get("farmer_id", "").strip()
    lang = request.args.get("lang", "en").strip().lower()
    limit = request.args.get("limit", "20").strip()
    try:
        limit_value = max(1, min(100, int(limit)))
    except ValueError:
        limit_value = 20

    rows = fetch_history(Config.DATABASE_PATH, farmer_id=farmer_id or None, limit=limit_value)
    results = []
    for row in rows:
        rec = get_recommendation_for_key(row["disease_key"])
        disease_name = rec["disease_name"].get(lang, rec["disease_name"]["en"])
        results.append(
            {
                "id": row["id"],
                "farmer_id": row["farmer_id"],
                "crop": row["crop"],
                "disease_key": row["disease_key"],
                "disease_name": disease_name,
                "confidence": row["confidence"],
                "weather_risk": row["weather_risk"],
                "created_at": row["created_at"],
            }
        )

    return jsonify({"count": len(results), "items": results})
