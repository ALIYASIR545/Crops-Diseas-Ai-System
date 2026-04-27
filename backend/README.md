# Backend - Smart Crop Disease Detection

## Run

1. Create virtual environment and activate.
2. Install:
   - `pip install -r requirements.txt`
3. Optional:
   - Copy `.env.example` to `.env`
4. Start:
   - `python app.py`

## Endpoints

- `GET /api/health`
- `POST /api/predict` (multipart form with `image`)
- `GET /api/history`
- `GET /api/weather-risk`
- `GET /api/alerts`

## Static Web UI

Open:

- `http://127.0.0.1:5000/`

## Model Notes

- Active trained model path: `backend/models/crop_disease_cnn.h5`
- Active label file: `backend/models/labels.json`
- Crop scope: Tomato, Potato, Maize
- If TensorFlow model cannot be loaded, API returns error by default.
  Set `ALLOW_FALLBACK_MODEL=true` only if you intentionally want demo fallback behavior.
