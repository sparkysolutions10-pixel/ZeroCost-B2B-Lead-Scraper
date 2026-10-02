import os
import requests
import json
import logging
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logger = logging.getLogger("mirofish.voice.vapi")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - VAPI - %(levelname)s - %(message)s')

class VapiDeploymentEngine:
    """
    Level 5 Architecture: AI Voice Receptionist Deployer.
    Uses the VAPI.ai REST API to instantly provision and configure human-like AI assistants
    for local businesses (Dentists, Real Estate, Clinics).
    """
    def __init__(self):
        # The user must set this in their environment variables later
        self.api_key = os.getenv("VAPI_PRIVATE_KEY", "YOUR_VAPI_API_KEY")
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_ai_assistant(self, business_name, role, custom_prompt):
        """Creates the Brain of the AI Receptionist."""
        logger.info(f"🧠 Provisioning AI Brain for: {business_name} ({role})")
        
        payload = {
            "name": f"{business_name} - {role}",
            "voice": {
                "provider": "11labs", # ElevenLabs for ultra-realistic voices
                "voiceId": "Rachel" # High-converting friendly female voice
            },
            "model": {
                "provider": "openai",
                "model": "gpt-4o", # Fastest latency
                "messages": [
                    {
                        "role": "system",
                        "content": custom_prompt
                    }
                ]
            },
            "firstMessage": f"Hi! Thank you for calling {business_name}. How can I help you today?",
            "recordingEnabled": True # For client QA and lead tracking
        }

        try:
            response = requests.post(f"{self.base_url}/assistant", headers=self.headers, json=payload)
            if response.status_code == 201:
                assistant_id = response.json().get("id")
                logger.info(f"✅ AI Assistant created successfully! ID: {assistant_id}")
                return assistant_id
            else:
                logger.error(f"❌ Failed to create assistant: {response.text}")
                return None
        except Exception as e:
            logger.error(f"⚠️ API Error: {str(e)}")
            return None

    def get_templates(self):
        """Pre-built AI personas we can sell instantly."""
        return {
            "Dental": """You are an enthusiastic and empathetic receptionist for a Dental Clinic. 
            Your goal is to book appointments for teeth cleaning and root canals. 
            Always ask for their name, phone number, and preferred time. 
            Be polite, sound 100% human, and use filler words like 'hmm' or 'let me check' naturally.""",
            
            "RealEstate": """You are a high-end real estate lead qualification agent.
            Your goal is to find out if the caller is looking to buy or sell a property, 
            their budget, and their timeline. Keep the conversation professional, confident, and persuasive."""
        }

    def deploy_client_system(self, client_name, niche):
        """The main orchestration function to build a client's system."""
        templates = self.get_templates()
        
        if niche not in templates:
            logger.error(f"Niche '{niche}' not found in templates.")
            return
            
        prompt = templates[niche]
        logger.info(f"🚀 [AGI ACTION] Initiating Deployment for {client_name} in {niche} niche...")
        
        assistant_id = self.create_ai_assistant(client_name, f"AI {niche} Receptionist", prompt)
        
        if assistant_id:
            logger.info("==================================================")
            logger.info(f" 💸 PRODUCT READY FOR {client_name.upper()}")
            logger.info(f" Assistant ID: {assistant_id}")
            logger.info(" Next Step: Purchase a Twilio phone number and link it via VAPI dashboard.")
            logger.info("==================================================")

if __name__ == "__main__":
    # Test the deployment logic
    engine = VapiDeploymentEngine()
    # Simulated Deployment (Will return Auth error until API key is set)
    engine.deploy_client_system("Dr. Smith Dental Care", "Dental")
