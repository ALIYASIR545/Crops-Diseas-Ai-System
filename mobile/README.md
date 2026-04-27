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

Configured in:

- `app/(tabs)/index.tsx`
- `app/(tabs)/explore.tsx`

Current defaults:

- Android emulator: `http://10.0.2.2:5000`
- iOS/Web: `http://127.0.0.1:5000`

If backend runs on another machine, replace with that machine's LAN IP.
