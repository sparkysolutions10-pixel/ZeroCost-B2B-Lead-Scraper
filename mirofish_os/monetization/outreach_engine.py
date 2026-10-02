import logging
import random
import sqlite3
import os
import time
import asyncio

logger = logging.getLogger("mirofish.monetization.outreach")

class AgencyOutreachEngine:
    """
    Sparky Digital Services - Autonomous Client Acquisition Engine.
    Includes Evolutionary A/B Testing for Subject Lines and Pitch Variations.
    """
    def __init__(self):
        self.base_payment_link = "https://razorpay.me/@sparkydigitalservices"
        self.db_path = os.path.join(os.path.dirname(__file__), "agency_crm.db")
        self._init_db()
        
        # Product Catalog
        self.services = {
            "basic_consultation": {"name": "AI Workflow Consultation", "min_price": 999, "max_price": 1999},
            "n8n_automation": {"name": "Custom Business Automation", "min_price": 4999, "max_price": 9999},
            "voice_agent": {"name": "AI Voice Receptionist (VAPI)", "min_price": 14999, "max_price": 24999},
        }
        
        # A/B Testing Variants
        self.subject_variants = {
            "A_Casual": "Quick question about {client_name}",
            "B_Urgent": "I found 500 leads for your business",
            "C_Value": "Free Custom Lead List for {client_name}"
        }
        
        self.pitch_variants = {
            "A_TrojanHorse": "Hi {client_name},\n\nI noticed you are expanding your business. Instead of sending a generic pitch, my AI already scraped 500 verified, hyper-targeted emails of your exact ideal customers.\n\n📊 FREE SAMPLE:\nI can send you a free sample of 50 leads to prove our data quality.\n\nOr, you can purchase the full verified database of 5000+ leads for INR {price} here: {payment_link}\n\nView our Data Portfolio: https://sparky-digital.netlify.app/\n\nBest,\nSparky Data Solutions",
            
            "B_AggressivePAS": "Hey {client_name},\n\nStop wasting time trying to find clients manually. It's expensive and slow.\n\nWe provide verified B2B email lists (Dentists, Real Estate, E-commerce) generated via custom AI scraping. \n\nOffer:\n1. 5000+ Verified Emails: INR {price}.\n2. Delivered in 24 hours as a clean CSV file.\n\nPurchase your custom list here: {payment_link}\n\nBest,\nSparky Data Solutions"
        }

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                email TEXT PRIMARY KEY,
                client_name TEXT,
                service_name TEXT,
                price INTEGER,
                payment_link TEXT,
                status TEXT,
                timestamp REAL,
                subject_variant TEXT,
                pitch_variant TEXT
            )
        ''')
        # Upgrade existing table with new A/B tracking columns if needed
        try:
            cursor.execute("ALTER TABLE leads ADD COLUMN subject_variant TEXT")
            cursor.execute("ALTER TABLE leads ADD COLUMN pitch_variant TEXT")
        except sqlite3.OperationalError:
            pass # Columns already exist
        conn.commit()
        conn.close()

    def _get_best_variants(self):
        """
        EVOLUTION LOGIC (Epsilon-Greedy Algorithm):
        Looks at the database to see which variants have 'PAID' status.
        70% of the time it uses the winning variant (Exploit).
        30% of the time it tries a random variant to discover better ones (Explore).
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check conversion rates
        cursor.execute("SELECT pitch_variant, COUNT(*) FROM leads WHERE status='PAID' AND pitch_variant IS NOT NULL GROUP BY pitch_variant")
        paid_pitches = dict(cursor.fetchall())
        
        cursor.execute("SELECT subject_variant, COUNT(*) FROM leads WHERE status='PAID' AND subject_variant IS NOT NULL GROUP BY subject_variant")
        paid_subjects = dict(cursor.fetchall())
        conn.close()
        
        # Self-Evolving Selection
        if paid_pitches and random.random() > 0.3:
            best_pitch = max(paid_pitches, key=paid_pitches.get)
        else:
            best_pitch = random.choice(list(self.pitch_variants.keys()))
            
        if paid_subjects and random.random() > 0.3:
            best_subject = max(paid_subjects, key=paid_subjects.get)
        else:
            best_subject = random.choice(list(self.subject_variants.keys()))
            
        return best_subject, best_pitch

    def _log_lead_to_crm(self, email, client_name, service_name, price, payment_link, subj_var, pitch_var):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO leads 
            (email, client_name, service_name, price, payment_link, status, timestamp, subject_variant, pitch_variant) 
            VALUES (?, ?, ?, ?, ?, 'UNPAID', ?, ?, ?)
        ''', (email, client_name, service_name, price, payment_link, time.time(), subj_var, pitch_var))
        conn.commit()
        conn.close()
        logger.info(f"💾 Saved lead {email} to Local CRM [Variant: {subj_var} | {pitch_var}]")

    def process_razorpay_webhook(self, webhook_email: str, amount_paid: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT client_name, service_name, price, subject_variant, pitch_variant FROM leads WHERE email=?", (webhook_email,))
        result = cursor.fetchone()
        
        if result:
            client_name, service_name, expected_price, subj_var, pitch_var = result
            cursor.execute("UPDATE leads SET status='PAID' WHERE email=?", (webhook_email,))
            conn.commit()
            logger.info(f"💰 MATCH FOUND! {client_name} paid for {service_name}. Variant {pitch_var} won!")
            self._trigger_fulfillment(client_name, webhook_email, service_name)
        conn.close()

    def _trigger_fulfillment(self, client_name, email, service_name):
        logger.info(f"🚀 AI Auto-Fulfillment Started for {client_name} -> {service_name}")

    def _determine_price_and_link(self, service_key: str) -> tuple[int, str]:
        service = self.services.get(service_key)
        price = random.randint(service["min_price"], service["max_price"])
        price = (price // 100) * 100 + 99
        payment_link = f"{self.base_payment_link}?amount={price}"
        return price, payment_link

    def generate_pitch(self, client_name: str, business_type: str, pain_point: str) -> dict:
        if "call" in pain_point.lower() or "support" in pain_point.lower():
            service_key = "voice_agent"
        elif "time" in pain_point.lower() or "manual" in pain_point.lower():
            service_key = "n8n_automation"
        else:
            service_key = "basic_consultation"
            
        service_name = self.services[service_key]["name"]
        price, payment_link = self._determine_price_and_link(service_key)
        
        # A/B Testing Evolution
        subj_variant_key, pitch_variant_key = self._get_best_variants()
        
        subject_line = self.subject_variants[subj_variant_key].format(client_name=client_name)
        
        pitch_template = self.pitch_variants[pitch_variant_key]
        pitch_message = pitch_template.format(
            client_name=client_name,
            pain_point=pain_point[:60],
            service_name=service_name,
            price=price,
            payment_link=payment_link
        )
        
        return {
            "client": client_name,
            "service_name": service_name,
            "pitch_text": pitch_message,
            "subject_line": subject_line,
            "payment_link": payment_link,
            "price": price,
            "subject_variant": subj_variant_key,
            "pitch_variant": pitch_variant_key
        }

    async def send_cold_email(self, recipient_email: str, pitch_data: dict):
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        sender_email = os.getenv("SMTP_EMAIL")
        sender_password = os.getenv("SMTP_PASSWORD")
        
        if not sender_email or not sender_password:
            return False

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = pitch_data.get("subject_line", f"AI Automation Solutions for {pitch_data['client']}")
        message.attach(MIMEText(pitch_data['pitch_text'], "plain"))

        try:
            loop = asyncio.get_running_loop()
            def _send():
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, message.as_string())
                server.quit()
                
            await loop.run_in_executor(None, _send)
            
            # Save to Local Database with Variant Info for Machine Learning
            self._log_lead_to_crm(
                recipient_email, 
                pitch_data["client"], 
                pitch_data["service_name"], 
                pitch_data["price"], 
                pitch_data["payment_link"],
                pitch_data["subject_variant"],
                pitch_data["pitch_variant"]
            )
            return True
        except Exception as e:
            return False

agency = AgencyOutreachEngine()
