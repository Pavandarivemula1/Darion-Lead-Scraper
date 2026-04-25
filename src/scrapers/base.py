from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any

class BaseScraper(ABC):
    @abstractmethod
    async def scrape(self, query: str) -> AsyncGenerator[Dict[str, Any], None]:
        pass
    
    @abstractmethod
    async def close(self):
        pass
