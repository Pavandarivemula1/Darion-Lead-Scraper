import re
from typing import Optional
import httpx
from src.utils.logger import get_logger

logger = get_logger(__name__)

class WhatsAppDetector:
    def __init__(self):
        self.wa_pattern = re.compile(r'wa\.me/|api\.whatsapp\.com/send|whatsapp\.com/channel')
        
    def extract_wa_links(self, html_content: str) -> bool:
        """Fallback to detect if webpage has wa.me links."""
        if not html_content:
            return False
            
        return bool(self.wa_pattern.search(html_content))
        
    def format_to_international(self, phone: str, default_country_code: str = "+91") -> str:
        """Basic phone formatter, assuming India by default as per 'Justdial/IndiaMART' context."""
        if not phone:
            return ""
            
        cleaned = re.sub(r'\D', '', phone)
        # Indian phone numbers
        if len(cleaned) == 10:
            return f"{default_country_code.strip('+')}{cleaned}"
        elif len(cleaned) == 12 and cleaned.startswith('91'):
            return cleaned
        return cleaned
        
    async def check_whatsapp_api(self, phone: str) -> bool:
        """
        In a real scenario, you'd use a Meta API token. 
        Here we format the wa.me link as proof of concept.
        """
        intl_phone = self.format_to_international(phone)
        if not intl_phone:
            return False
            
        # Simulating detection by generating outreach link
        self.outreach_url = f"https://wa.me/{intl_phone}"
        logger.info(f"Generated WA link: {self.outreach_url}")
        
        # We assume false generally unless detected in HTML, to maximize the 'no WA' score.
        return False
