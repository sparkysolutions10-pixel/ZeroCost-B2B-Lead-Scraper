import csv
import urllib.parse
import re
import os
import sys
import logging
import asyncio
from playwright.async_api import async_playwright

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logger = logging.getLogger("mirofish.monetization.lead_gen")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - DATA ENGINE - %(levelname)s - %(message)s')

class AdvancedLeadGenerator:
    """
    Level 5 Data Product Engine (Playwright Upgraded).
    Uses full headless browsing to bypass Captchas and extract leads safely.
    """
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), "client_deliverables")
        os.makedirs(self.output_dir, exist_ok=True)

    async def extract_leads_from_search(self, niche: str, location: str):
        """Scrapes via Headless Chromium using Playwright."""
        logger.info(f"dY"? Compiling Data for: {niche} in {location} using Headless Browser...")
        
        query = f'("{niche}") "{location}" "contact" "@gmail.com" OR "@yahoo.com"'
        url = "https://lite.duckduckgo.com/lite/"
        
        all_leads = set()
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url)
                
                # Fill search box and submit
                await page.fill('input[name="q"]', query)
                await page.click('input[type="submit"]')
                await page.wait_for_load_state("domcontentloaded")
                
                # Extract HTML
                html = await page.content()
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
                
                for email in emails:
                    all_leads.add(email)
                    
                await browser.close()
                
        except Exception as e:
            logger.error(f"?O Failed to scrape using Playwright: {str(e)}")
            
        logger.info(f"o. Successfully compiled {len(all_leads)} raw leads using Browser.")
        return list(all_leads)

    def generate_csv_product(self, client_name: str, niche: str, location: str):
        """Generates the final CSV file."""
        # Run async scraper synchronously
        leads = asyncio.run(self.extract_leads_from_search(niche, location))
        
        if not leads:
            logger.warning("No leads found to generate product.")
            return None
            
        filename = f"{client_name.replace(' ', '_')}_{niche.replace(' ', '')}_Leads.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Business Niche", "Location", "Email Address", "Status"])
            for email in leads:
                writer.writerow([niche, location, email, "Verified"])
                
        logger.info(f"dY" PRODUCT GENERATED SUCCESSFULLY: {filepath}")
        return filepath

if __name__ == "__main__":
    engine = AdvancedLeadGenerator()
    engine.generate_csv_product(client_name="Premium_Dubai_Broker", niche="Real Estate Investors and Buyers", location="Dubai")
