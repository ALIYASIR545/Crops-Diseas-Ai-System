# Smart Crop Disease AI System (Pakistan FYP)

This project now includes a complete prototype with:

- Flask backend API for image-based disease prediction
- Recommendation engine (pesticide, dosage, treatment, prevention)
- English and Urdu responses
- SQLite disease history tracking
- Weather-based risk estimation
- Real-time alerts API
- Web interface (`backend/static/index.html`)
- Expo mobile app (`mobile/`) connected to backend APIs

## Project Structure

```text
crop-disease-ai-system/
  backend/
    app.py
    config.py
    requirements.txt
    routes/
    utils/
    models/
    data/
    static/
  dataset/
    train/
    validation/
    test/
  mobile/
    app/
    package.json
```

## Backend Setup

1. Open terminal in `backend/`.
2. Create virtual environment and activate it.
3. Install dependencies:
   - `pip install -r requirements.txt`
4. (Optional) Copy `.env.example` to `.env` and update values.
5. Start server:
   - `python app.py`

Backend runs on `http://127.0.0.1:5000`.

### Main API Endpoints

- `GET /api/health`
- `POST /api/predict` (multipart key: `image`)
- `GET /api/history?farmer_id=farmer-001&limit=20&lang=en`
- `GET /api/weather-risk?latitude=31.52&longitude=74.35&disease_key=Tomato___Late_blight`
- `GET /api/alerts`

## Model Training (PlantVillage)

Train directly from class folders (for tomato, potato, maize), then run:

```bash
python backend/models/train_kaggle_model.py \
  --data-dir dataset/tomato_potato_maize \
  --output-model backend/models/crop_disease_cnn.h5 \
  --output-labels backend/models/labels.json \
  --output-summary backend/models/training_summary.json \
  --dataset-source "combined: kaggle emmarex/plantdisease + soumiknafiul/plantvillage-dataset-labeled" \
  --epochs 8 \
  --fine-tune-epochs 2
```

Current trained model is configured for these crops only:
- Tomato
- Potato
- Maize

By default, backend requires a trained TensorFlow model and does not use heuristic fallback
(`ALLOW_FALLBACK_MODEL=false`).

## Web App

Open:

- `http://127.0.0.1:5000/`

Upload leaf image and get disease result with recommendations.

## Mobile App Setup

1. Open terminal in `mobile/`.
2. Install dependencies:
   - `pnpm install`
3. Start Expo:
   - `pnpm start`

### Mobile Backend URL

Configured in:

- `mobile/app/(tabs)/index.tsx`
- `mobile/app/(tabs)/explore.tsx`

Current default:

- Android emulator: `http://10.0.2.2:5000`
- iOS/Web: `http://127.0.0.1:5000`

Change it if your backend runs on another machine IP.

## Notes

- Recommendation data is in `backend/data/disease_recommendations.json`.
- Alert samples are in `backend/data/outbreak_alerts.json`.
- Prediction history DB is auto-created at `backend/data/app.db`.
- Uploads are saved in `backend/uploads/`.
