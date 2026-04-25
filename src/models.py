from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from enum import Enum

class Priority(str, Enum):
    HIGH = "High"
    MEDIUM_HIGH = "Medium-High"
    MEDIUM = "Medium"
    LOW = "Low"

class Lead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(None, alias="_id")
    business_name: str
    category: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = 0
    social_links: List[str] = Field(default_factory=list)
    
    has_whatsapp: bool = False
    is_website_poor: bool = False
    
    score: int = 0
    priority: Priority = Priority.LOW
