# Smart Crop AI Deployment Guide (Beginner Friendly)

This guide is for your current project state on **April 29, 2026**.

You will deploy:
- Backend + web UI on Render
- Android APK with Expo EAS
- Optional monetization setup (AdMob + AdSense)

---

## 1) Before You Start

You need accounts:
- GitHub
- Render
- Expo
- Google Play Console (for publishing app later)
- Google AdMob (for app earnings)
- Google AdSense (for web earnings)

Install on your PC:
- Git
- Node.js
- pnpm

---

## 2) Push Project to GitHub

From project root:

```bash
git init
git add .
git commit -m "Production-ready crop disease system"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

---

## 3) Deploy Backend + Web on Render

Your Flask app already serves:
- Web UI at `/`
- API at `/api/*`

### A) Create service
1. Open Render dashboard.
2. Click `New` -> `Web Service`.
3. Connect your GitHub repo.
4. Use these settings:
   - Name: `crop-disease-backend`
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 180`

### B) Environment variables
Set these in Render:
- `DEBUG=false`
- `SECRET_KEY=<long-random-string>`
- `ALLOW_FALLBACK_MODEL=false`
- `WEATHER_API_URL=https://api.open-meteo.com/v1/forecast`
- `WEATHER_TIMEOUT_SECONDS=8`

### C) Deploy and verify
After deploy, test:
- `https://<your-render-domain>/api/health`
- `https://<your-render-domain>/`

Health response should show:
- `"using_trained_model": true`
- `"supported_crops": ["maize","potato","tomato"]`

---

## 4) Important Model Files in Production

Required files must exist in backend deploy:
- `backend/models/crop_disease_cnn.h5`
- `backend/models/labels.json`
- `backend/models/training_summary.json`

If missing, prediction will fail (fallback is disabled intentionally).

---

## 5) Configure Mobile to Use Production API

You already have environment support in app code.

Set production URL in:
- `mobile/eas.json` -> `EXPO_PUBLIC_API_BASE_URL`

Replace:
- `https://your-backend-domain.onrender.com`

With your real Render URL:
- `https://crop-disease-backend.onrender.com` (example)

---

## 6) Build Android APK (Installable File)

From `mobile` folder:

```bash
pnpm add -g eas-cli
eas login
eas build:configure
eas build -p android --profile preview
```

Result:
- Preview profile generates APK for direct install/testing.

For Play Store release:

```bash
eas build -p android --profile production
```

This usually generates AAB (Play Store format).

---

## 7) Monetization (How You Earn)

## Mobile app earnings (AdMob)
1. Create AdMob account.
2. Add Android app in AdMob.
3. Create ad units (banner/interstitial/rewarded).
4. Integrate ads in app screens.
5. Publish app and increase installs.

## Web earnings (AdSense)
1. Create AdSense account.
2. Add your deployed domain.
3. Verify ownership.
4. Add ad script/placements in web UI.

Note:
- Ad networks approve faster when app/site has real users and clear content.

---

## 8) Free Tier Reality (Important)

Free tiers are good for launch/testing, but:
- Can sleep/slow on inactivity.
- Might not be reliable for heavy real users.

When users grow, move to paid always-on plan.

---

## 9) Troubleshooting

## `api/health` shows `using_trained_model: false`
- Model files missing in deploy.
- TensorFlow install failed.

## Weather risk says API unavailable
- Temporary DNS/network issue on host.
- Retry later; detection still works.

## Expo build fails
- Ensure `eas.json` exists.
- Ensure `EXPO_PUBLIC_API_BASE_URL` is valid HTTPS URL.

---

## 10) Your Next Step

Do this now in order:
1. Push repo to GitHub
2. Create Render Web Service
3. Set env vars
4. Share your Render URL
5. Build APK with EAS

After you share your Render URL, we can finalize mobile production link in one step.
