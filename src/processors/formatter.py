from src.models import Lead

class MessageFormatter:
    def __init__(self):
        self.templates = {
            "no_website": "Hi {name}, I noticed your business is doing well in {category} but doesn't have a modern website. We help local businesses establish a digital presence. Would you be open to a quick chat?",
            "no_whatsapp": "Hi {name}, a lot of {category} businesses are using WhatsApp automation to capture leads. Would you like a free demo on how it can work for you?",
            "general": "Hi {name}, I found your business and saw some potential to boost your local rankings and customer engagement. Open to discussing some ideas?"
        }
        
    def generate_message(self, lead: Lead) -> str:
        name = lead.business_name or "there"
        category = lead.category or "your industry"
        
        if not lead.website or lead.is_website_poor:
            return self.templates["no_website"].format(name=name, category=category)
        elif not lead.has_whatsapp:
            return self.templates["no_whatsapp"].format(name=name, category=category)
        else:
            return self.templates["general"].format(name=name, category=category)

