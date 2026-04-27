import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", "8")) * 1024 * 1024

    MODEL_PATH = Path(os.getenv("MODEL_PATH", BASE_DIR / "models" / "crop_disease_cnn.h5"))
    LABELS_PATH = Path(os.getenv("LABELS_PATH", BASE_DIR / "models" / "labels.json"))
    TRAINING_SUMMARY_PATH = Path(
        os.getenv("TRAINING_SUMMARY_PATH", BASE_DIR / "models" / "training_summary.json")
    )
    RECOMMENDATIONS_PATH = Path(
        os.getenv("RECOMMENDATIONS_PATH", BASE_DIR / "data" / "disease_recommendations.json")
    )
    ALERTS_PATH = Path(os.getenv("ALERTS_PATH", BASE_DIR / "data" / "outbreak_alerts.json"))
    DATABASE_PATH = Path(os.getenv("DATABASE_PATH", BASE_DIR / "data" / "app.db"))
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))

    WEATHER_API_URL = os.getenv(
        "WEATHER_API_URL",
        "https://api.open-meteo.com/v1/forecast",
    )
    WEATHER_TIMEOUT_SECONDS = int(os.getenv("WEATHER_TIMEOUT_SECONDS", "8"))
    ALLOW_FALLBACK_MODEL = os.getenv("ALLOW_FALLBACK_MODEL", "false").lower() == "true"
