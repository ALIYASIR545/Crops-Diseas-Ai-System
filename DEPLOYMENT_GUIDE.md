# Deployment Guide for Crop Disease AI System

This guide covers deploying both the **Backend (Flask)** and **Mobile Web** apps for free.

---

## 🚀 Option 1: Render (Best for Backend)

### Why Render?
- **Free tier**: 750 hours/month
- **Python support**: Native
- **TensorFlow**: Works with CPU tier

### Steps to Deploy Backend:

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   # Create repo on GitHub and push
   ```

2. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

3. **Create a Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repo
   - Configure:
     - **Name**: `crop-disease-backend`
     - **Root Directory**: `backend`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
   - **Free** tier selected

4. **Environment Variables**
   Add these in Render dashboard:
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secret-key
   ```

5. **Deploy!** 
   - Your API will be live at: `https://crop-disease-backend.onrender.com`

---

## 🌐 Option 2: Vercel (Best for Mobile Web)

### Why Vercel?
- **Free tier**: Unlimited projects
- **Great for**: Expo/React Native web
- **CDN**: Fast global delivery

### Steps to Deploy Mobile Web:

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Create `vercel.json` in mobile folder**
   ```json
   {
     "build": {
       "output": "dist",
       "command": "npx expo export --platform web"
     },
     "install": {
       "command": "pnpm install"
     },
     "framework": "expo"
   }
   ```

3. **Deploy**
   ```bash
   cd mobile
   vercel
   ```
   - Follow prompts
   - Your web app will be live at: `https://your-project.vercel.app`

---

## 📱 Option 3: EAS Build (For Android APK)

### Why EAS?
- **Free tier**: 30 build minutes/month
- **Output**: Installable APK

### Steps:
```bash
cd mobile

# Install EAS CLI
npm i -g eas-cli

# Login
eas login

# Configure
eas build -p android --profile preview

# Download APK from EAS dashboard
```

---

## 🔗 Connecting Mobile to Backend

After deploying, update your mobile app to point to your backend:

**File**: `mobile/app/config.ts` (create if needed)
```typescript
export const API_BASE_URL = 'https://crop-disease-backend.onrender.com/api';
```

---

## 📋 Quick Summary

| Component | Platform | URL Example |
|-----------|----------|-------------|
| Backend API | Render | `crop-disease-backend.onrender.com` |
| Mobile Web | Vercel | `crop-disease-mobile.vercel.app` |
| Android APK | EAS Build | Download from EAS dashboard |

---

## ⚠️ Important Notes

1. **Cold Start**: Free tiers may take 30-60 seconds to start after inactivity
2. **TensorFlow**: Use `tensorflow-cpu` (already in requirements.txt) for free tier
3. **Database**: SQLite works on Render but resets on each deploy. Consider using PostgreSQL for production

---

## ✅ Next Steps

1. Push code to GitHub
2. Deploy backend to Render
3. Deploy mobile web to Vercel
4. Update mobile config to point to backend
5. Share your URLs!