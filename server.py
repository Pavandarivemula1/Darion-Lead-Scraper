from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import glob
import os
import pandas as pd
from main import orchestrate
import asyncio

app = FastAPI(title="AntiGravity Lead Generation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    city: str
    category: str
    max_results: int

@app.post("/api/scrape")
async def start_scrape(req: ScrapeRequest, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(orchestrate, req.city, req.category, req.max_results)
        return {
            "status": "started", 
            "message": f"Started scraping up to {req.max_results} {req.category} in {req.city}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leads")
async def list_datasets():
    files = sorted(glob.glob("leads_*.csv"), key=os.path.getmtime, reverse=True)
    return {"datasets": files}

@app.get("/api/leads/{filename}")
async def get_dataset(filename: str):
    # Security check to prevent path traversal
    if not filename.startswith("leads_") or not filename.endswith(".csv") or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
        
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    try:
        df = pd.read_csv(filename)
        # Convert NaN/Infinity to primitive types compatible with JSON
        df = df.fillna("")
        
        # Calculate premium metrics
        total = len(df)
        high_quality = len(df[df.get('score', 0) >= 70]) if 'score' in df.columns else 0
        wa_available = len(df[df.get('has_whatsapp', False) == True]) if 'has_whatsapp' in df.columns else 0
        
        metrics = {
            "total": total,
            "high_quality": high_quality,
            "whatsapp": wa_available
        }
        
        return {
            "metrics": metrics,
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read data: {str(e)}")

# Mount static files at root
app.mount("/", StaticFiles(directory="public", html=True), name="public")
