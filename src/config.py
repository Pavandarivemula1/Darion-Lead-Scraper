import os

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = "lead_gen_db"
    COLLECTION_NAME = "leads"
    
    # Timeouts
    SCRAPE_TIMEOUT = 30000
