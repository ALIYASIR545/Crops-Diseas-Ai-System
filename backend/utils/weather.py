from typing import Any, Dict, Optional

import requests

from config import Config


def _to_float(value: Optional[str]) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _risk_level(temp: float, humidity: float, precipitation: float) -> str:
    if humidity >= 80 and 18 <= temp <= 32:
        return "high"
    if humidity >= 65 or precipitation > 2:
        return "medium"
    return "low"


def get_weather_risk(
    latitude: Optional[str],
    longitude: Optional[str],
    disease_key: str = "",
) -> Dict[str, Any]:
    lat = _to_float(latitude)
    lon = _to_float(longitude)
    if lat is None or lon is None:
        return {
            "available": False,
            "risk_level": "unknown",
            "message": "Weather risk skipped. Add latitude and longitude for climate-based risk.",
        }

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
    }

    try:
        response = requests.get(
            Config.WEATHER_API_URL,
            params=params,
            timeout=Config.WEATHER_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        current = payload.get("current", {})
        temp = float(current.get("temperature_2m", 0.0))
        humidity = float(current.get("relative_humidity_2m", 0.0))
        precipitation = float(current.get("precipitation", 0.0))
        wind = float(current.get("wind_speed_10m", 0.0))
        risk = _risk_level(temp=temp, humidity=humidity, precipitation=precipitation)

        if disease_key and "blight" in disease_key.lower() and risk == "medium":
            risk = "high"

        return {
            "available": True,
            "risk_level": risk,
            "temperature_c": round(temp, 1),
            "humidity_percent": round(humidity, 1),
            "precipitation_mm": round(precipitation, 2),
            "wind_kmh": round(wind, 1),
        }
    except Exception as exc:
        return {
            "available": False,
            "risk_level": "unknown",
            "message": f"Weather API unavailable: {exc}",
        }
