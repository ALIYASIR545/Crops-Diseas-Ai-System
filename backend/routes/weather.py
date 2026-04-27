from flask import Blueprint, jsonify, request

from utils.weather import get_weather_risk

weather_bp = Blueprint("weather", __name__)


@weather_bp.get("/weather-risk")
def weather_risk():
    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")
    disease_key = request.args.get("disease_key", "")

    if latitude is None or longitude is None:
        return (
            jsonify({"error": "latitude and longitude query params are required"}),
            400,
        )

    risk = get_weather_risk(latitude=latitude, longitude=longitude, disease_key=disease_key)
    return jsonify(risk)
