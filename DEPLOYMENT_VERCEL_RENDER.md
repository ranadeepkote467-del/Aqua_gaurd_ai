# AquaGuard AI Deployment Guide

This guide deploys:
- Backend (Flask + model): Render
- Frontend (static UI): Vercel

## 1) What is already prepared in this repo

The following deployment-ready changes are in place:
- `requirements.txt` includes all needed packages (including `requests`, `xgboost`, `flask-cors`, `gunicorn`)
- `app.py` supports production host/port (`0.0.0.0` + `PORT`) and CORS configuration via environment variable
- `services/weather.py` uses `OPENWEATHER_API_KEY` from environment variables (no hardcoded key)

## 2) Deploy Backend on Render

### Step 1: Push your project to GitHub
If your latest local changes are not pushed yet, push them first.

### Step 2: Create Web Service on Render
1. Open Render dashboard.
2. Click New + -> Web Service.
3. Connect your GitHub repo.
4. Configure:
   - Runtime: Python 3
   - Region: pick nearest to your users
   - Branch: main (or your deployment branch)
   - Root Directory: leave empty (project root)

### Step 3: Set Build and Start commands
- Build Command:

  pip install -r requirements.txt && python train.py

- Start Command:

  gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120

Why `python train.py` in build?
- Your `.gitignore` excludes model files in `models/*.pkl`.
- Render must generate `models/flood_model.pkl` during build.

### Step 4: Add environment variables in Render
Add these in Render -> Environment:
- `OPENWEATHER_API_KEY` = your OpenWeather key
- `CORS_ORIGINS` = your Vercel domain (example: `https://your-frontend.vercel.app`)
- Optional: `FLASK_DEBUG=false`

### Step 5: Deploy and test backend
After deployment, note your Render URL, for example:
- `https://aquaguard-backend.onrender.com`

Quick test:
- Open backend URL in browser. Home page should load.

## 3) Prepare Frontend for Vercel

Your current `templates/index.html` is a Flask/Jinja template. Vercel static hosting needs plain HTML.

Create a frontend folder and static files:

1. Create folder:
- `frontend/`

2. Copy and edit files:
- Copy `templates/index.html` -> `frontend/index.html`
- Copy `static/style.css` -> `frontend/style.css`

3. In `frontend/index.html`, make these edits:
- Replace stylesheet line:

  From:
  {{ url_for('static', filename='style.css') }}

  To:
  ./style.css

- Add your Render backend URL in script:

  const API_BASE = "https://your-render-service.onrender.com";

- Update weather API fetch:

  From:
  fetch("/weather", ...)

  To:
  fetch(`${API_BASE}/weather`, ...)

- Update prediction form action so submit goes to backend:

  Add this once after page load:

  document.querySelector("form").action = `${API_BASE}/predict`;

Notes:
- When user submits the form from Vercel, result page will be served by Render (`/predict` response).
- This is expected for your current Flask template workflow.

## 4) Deploy Frontend on Vercel

1. Open Vercel dashboard.
2. Click Add New -> Project.
3. Import the same GitHub repo.
4. Configure project:
   - Framework preset: Other
   - Root Directory: `frontend`
   - Build Command: leave empty
   - Output Directory: leave default / empty for static files
5. Deploy.

After deployment, you get URL like:
- `https://your-frontend.vercel.app`

## 5) Final wiring checklist

1. Copy your Vercel URL.
2. Put it in Render env var `CORS_ORIGINS`.
3. Redeploy Render service.
4. Open Vercel URL and test:
   - Get Current Weather button
   - Predict Flood Risk submission

## 6) Troubleshooting

### Error: CORS blocked in browser
- Ensure `CORS_ORIGINS` in Render exactly matches Vercel domain, including `https://`
- Redeploy Render after env var change

### Error: model file missing on Render
- Ensure Build Command includes `python train.py`
- Check Render build logs for training completion

### Weather returns error
- Verify `OPENWEATHER_API_KEY` is set and valid
- Check Render logs for `/weather` request errors

### Slow first request on free tier
- Render free instances may sleep when idle. First request can take time.

## 7) Recommended production improvements

- Move weather and prediction to JSON API endpoints for a cleaner frontend-backend split
- Add basic rate limiting for API routes
- Add monitoring/alerts (Render logs + uptime monitor)
- Consider a paid Render plan to avoid cold starts
