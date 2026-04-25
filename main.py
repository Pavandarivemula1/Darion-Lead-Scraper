import asyncio
import argparse
from typing import List

from src.scrapers.google_maps import GoogleMapsScraper
from src.processors.qualifier import LeadQualifier
from src.processors.whatsapp import WhatsAppDetector
from src.processors.formatter import MessageFormatter
from src.storage.db import DatabaseUnit
from src.storage.exporter import DataExporter
from src.models import Lead
from src.utils.logger import get_logger

logger = get_logger("main")

async def orchestrate(city: str, category: str, max_results: int = 20):
    query = f"{category} in {city}"
    
    scraper = GoogleMapsScraper(headless=True)
    qualifier = LeadQualifier()
    wa_detector = WhatsAppDetector()
    formatter = MessageFormatter()
    
    db = DatabaseUnit()
    use_db = False
    try:
        await db.init_db()
        use_db = True
    except Exception as e:
        logger.warning(f"Could not connect to MongoDB. It may not be running locally. Skipping DB deduplication. Details: {e}")
        use_db = False
        
    leads: List[Lead] = []
    
    try:
        async for raw_item in scraper.scrape(query=query, max_results=max_results):
            # Qualify Lead
            lead = qualifier.qualify(raw_item)
            
            # WA detection (heuristics via website)
            has_wa_link = wa_detector.extract_wa_links(raw_item.get("website", ""))
            lead.has_whatsapp = has_wa_link
            
            # Re-qualify score with WA stat added
            if not lead.has_whatsapp:
                lead.score = min(lead.score + 25, 100)
            
            # Formatter message
            message = formatter.generate_message(lead)
            logger.info(f"Lead [{lead.priority.value} - Score: {lead.score}]: {lead.business_name} | Message template generated.")
            
            leads.append(lead)
            
            # Save to Db
            if use_db:
                await db.save_lead(lead)
                
    finally:
        await scraper.close()
        if use_db:
            await db.close()
            
    # Export all
    if leads:
        filename = f"leads_{city.lower().replace(' ', '_')}.csv"
        DataExporter.export_csv(leads, filename)
        logger.info(f"Run completed. Exported {len(leads)} leads to {filename}")
    else:
        logger.info("No leads found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="High-Scale Lead Generation System")
    parser.add_argument("--city", type=str, default="London", help="City to search in")
    parser.add_argument("--category", type=str, default="Plumbers", help="Business category")
    parser.add_argument("--max", type=int, default=10, help="Max results to scrape")
    
    args = parser.parse_args()
    
    logger.info("Starting Scrape Job...")
    asyncio.run(orchestrate(args.city, args.category, args.max))
