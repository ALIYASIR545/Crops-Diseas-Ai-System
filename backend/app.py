from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import Config
from routes.alerts import alerts_bp
from routes.health import health_bp
from routes.history import history_bp
from routes.predict import predict_bp
from routes.weather import weather_bp
from utils.db import init_db


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static")
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.config["UPLOAD_DIR"] = Config.UPLOAD_DIR
    app.config["UPLOAD_DIR"].mkdir(parents=True, exist_ok=True)
    init_db(Config.DATABASE_PATH)

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(predict_bp, url_prefix="/api")
    app.register_blueprint(history_bp, url_prefix="/api")
    app.register_blueprint(weather_bp, url_prefix="/api")
    app.register_blueprint(alerts_bp, url_prefix="/api")

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Route not found"}), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
