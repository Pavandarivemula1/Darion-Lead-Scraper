import re
from typing import Dict, Any
from src.models import Lead, Priority

class LeadQualifier:
    def __init__(self):
        self.personal_emails = ["@gmail.com", "@yahoo.com", "@hotmail.com", "@outlook.com"]
        
    def qualify(self, raw_data: Dict[str, Any]) -> Lead:
        lead = Lead(**raw_data)
        score = 0
        
        # 1. Digital Presence Check
        if not lead.website:
            score += 40
            lead.is_website_poor = True
        else:
            # Check for generic websites or long complex urls mapping to basic builders
            if any(domain in lead.website.lower() for domain in ["wixsite", "wordpress.com", "blogspot"]):
                score += 20
                lead.is_website_poor = True
                
        # 2. Review Count / Activity
        if lead.review_count is not None and lead.review_count > 0:
            if lead.review_count < 50:
                score += 15 # active but low presence
        elif lead.review_count is None or lead.review_count == 0:
            score += 10 # very low presence
            
        # 3. WhatsApp & Contact Info
        if not lead.has_whatsapp:
            score += 25
            
        if lead.email and any(pe in lead.email.lower() for pe in self.personal_emails):
            score += 10 # Unprofessional email
            
        lead.score = min(score, 100)
        
        # Determine Priority
        if lead.score >= 70:
            lead.priority = Priority.HIGH
        elif lead.score >= 50:
            lead.priority = Priority.MEDIUM_HIGH
        elif lead.score >= 30:
            lead.priority = Priority.MEDIUM
        else:
            lead.priority = Priority.LOW
            
        return lead
