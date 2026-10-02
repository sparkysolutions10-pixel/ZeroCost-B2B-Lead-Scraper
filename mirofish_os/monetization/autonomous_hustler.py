import urllib.request
import urllib.parse
import json
import time
import os
import sys
import logging

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Structured Logging instead of print()
logger = logging.getLogger("mirofish.monetization.hustler")

root_dir = r"C:\Users\tarun\Downloads\MiroFish-main (1)\MiroFish-main"
sys.path.append(os.path.join(root_dir, "mirofish_os", "monetization"))

from outreach_engine import agency

def run_autonomous_campaign():
    logger.info("[Sparky Auto-Hustler] Initiating Level 5 Autonomous Campaign...")
    
    # 1. SCRAPE REAL BUSINESS EMAILS (DuckDuckGo Lite)
    logger.info("[Step 1] Scraping DuckDuckGo for Dubai Real Estate Brokers...")
    
    url = f"https://lite.duckduckgo.com/lite/"
    # Highly targeted Dork for Dubai brokers
    data = urllib.parse.urlencode({'q': '("real estate broker" OR "property consultant") "Dubai" "@gmail.com" OR "@yahoo.com"'}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    complaints = []
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            
            import re
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
            emails = list(set(emails))
            
            for email in emails[:3]:
                complaints.append({
                    "source": "SearchEngine",
                    "user": email.split('@')[0].capitalize(),
                    "email": email,
                    "complaint": "Manual workflows and high operational costs."
                })
    except Exception as e:
        logger.error(f"Error scraping real emails: {e}")
        raise # Reraise for the daemon to catch and apply exponential backoff
        
    logger.info(f"SUCCESS: Found {len(complaints)} fresh leads.")

    # 2. OUTREACH ENGINE
    import asyncio
    
    async def process_leads():
        for lead in complaints:
            logger.info(f"[Step 2] Processing lead: {lead['user']}")
            
            # Use AI Engine to generate customized pitch
            pitch_data = agency.generate_pitch(
                client_name=lead["user"],
                business_type="Local Business",
                pain_point=lead["complaint"]
            )
            
            # Send Email
            success = await agency.send_cold_email(lead["email"], pitch_data)
            
            if success:
                logger.info(f"Successfully pitched {lead['user']} via {lead['email']}")
            else:
                logger.warning(f"Failed to send email to {lead['email']}. SMTP issue?")
                
            await asyncio.sleep(2) # Anti-spam delay between emails
            
    # Run the async outreach if we have leads
    if complaints:
        asyncio.run(process_leads())
    else:
        logger.warning("No leads found this cycle.")

if __name__ == "__main__":
    run_autonomous_campaign()
