from motor.motor_asyncio import AsyncIOMotorClient
from src.config import Config
from src.models import Lead
from src.utils.logger import get_logger

logger = get_logger(__name__)

class DatabaseUnit:
    def __init__(self):
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        self.collection = self.db[Config.COLLECTION_NAME]
        
    async def init_db(self):
        # Create an index on phone_number for deduplication
        await self.collection.create_index("phone_number", unique=True, sparse=True)
        # Create index on website
        await self.collection.create_index("website", unique=True, sparse=True)
        logger.info("Database indexes initialized")
        
    async def save_lead(self, lead: Lead) -> bool:
        doc = lead.model_dump(by_alias=True, exclude_none=True)
        doc.pop("_id", None) # Remove None ID
        
        try:
            # Deduplicate by phone number or website if available
            query = {"$or": []}
            if lead.phone_number:
                query["$or"].append({"phone_number": lead.phone_number})
            if lead.website:
                query["$or"].append({"website": lead.website})
                
            if query["$or"]:
                existing = await self.collection.find_one(query)
                if existing:
                    # Optional: update score if this one is better, or just skip
                    logger.debug(f"Lead {lead.business_name} already exists. Skipping.")
                    return False
                    
            await self.collection.insert_one(doc)
            logger.info(f"Saved lead: {lead.business_name} (Score: {lead.score})")
            return True
        except Exception as e:
            logger.error(f"Error saving lead {lead.business_name}: {e}")
            return False
            
    async def close(self):
        self.client.close()
