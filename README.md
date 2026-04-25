# Darion Lead Generation System (AntiGravity)

A high-scale lead generation engine designed to identify businesses that require digital presence (websites) or WhatsApp automation services. The system utilizes headless Chrome scraping to ingest high-value business leads, score them algorithmically 1-100, and present them in a premium web dashboard.

## 🏗️ Decoupled Architecture

This application employs a split production architecture to circumvent heavy Cloud timeouts:
1. **Frontend (Vercel)**: Based entirely inside the `public/` directory. It is a stunning, glassmorphic static HTML/CSS/JS interface packed with Light/Dark mode toggling and instant CSV downloading built via FastAPI calls.
2. **Backend (Render, Railway)**: A `FastAPI` instance (`server.py`) acting as the API layer encapsulating `main.py`. This layer natively handles long-lived scraping operations that standard Vercel serverless functions natively block.

---

## 💻 Local Development

### 1. Prerequisites
- Python 3.9+
- MongoDB (Optional, for deduplication. If unavailable, CSV extraction still works beautifully).

### 2. Environment Initialization
```bash
# Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate

# Install all required logic & API packages
pip install -r requirements.txt

# Crucial: Install Chromium browser binaries for infinite scroll
playwright install chromium
```

### 3. Launching the Web Portal
Instead of directly hitting terminal commands, invoke the `uvicorn` development server. This runs your API backend and seamlessly serves the static UI payload immediately at your `localhost`.
```bash
uvicorn server:app --reload
```
Open **[http://localhost:8000](http://localhost:8000)** to view the dashboard!

*(Alternatively: headless terminal execution remains supported via `python main.py --city "London" --category "Plumbers" --max 10`).*

---

## 🚀 Production Deployment Guide

### Backend → Render
Deploy your heavy-lifting API backend securely:
1. Push this repository to GitHub natively.
2. Connect your Render account and spin up a new **Web Service**.
3. The custom `Dockerfile` already natively forces Render to install Microsoft's official Playwright libraries and serve `uvicorn`. Choose **Docker** as your environment.
4. Copy the output deployment web address (e.g. `https://darion-scraper.onrender.com`).

### Frontend → Vercel
Deploy your gorgeous static UI for extreme speed and global caching:
1. Go to Vercel, attach this SAME GitHub repository, and start a deployment.
2. The included `vercel.json` already natively halts Vercel's aggressive Python/FastAPI builders! It will immediately build pure static files from your `/public` folder.
3. Once your Render Backend is live, edit `/public/script.js` (Line 60):
   ```javascript
   const API_BASE = "https://darion-scraper.onrender.com";
   ```
4. Push that edit to Git. Vercel automatically deploys it!
