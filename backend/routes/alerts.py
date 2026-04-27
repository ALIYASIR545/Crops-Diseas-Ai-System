import json

from flask import Blueprint, jsonify

from config import Config

alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.get("/alerts")
def alerts():
    if not Config.ALERTS_PATH.exists():
        return jsonify({"count": 0, "items": []})

    with Config.ALERTS_PATH.open("r", encoding="utf-8") as fp:
        items = json.load(fp)
    return jsonify({"count": len(items), "items": items})
