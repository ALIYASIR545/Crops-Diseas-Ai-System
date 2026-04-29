# Smart Crop Disease Mobile App (Expo)

This app is the mobile client for the Smart Crop Disease Detection System.

## Features

- Leaf image upload and AI disease detection
- English and Urdu interface
- Confidence score and treatment recommendations
- Detection history tracking
- Outbreak alerts display

## Run

1. Install dependencies:
   - `pnpm install`
2. Start the app:
   - `pnpm start`

## Backend API URL

API base URL is now read from env variable:

- `EXPO_PUBLIC_API_BASE_URL`

Configured for build profiles in:

- `eas.json`

Fallback local defaults (if env var not set):

- Android emulator: `http://10.0.2.2:5000`
- iOS/Web: `http://127.0.0.1:5000`
