import asyncio
import os
import sys
from dotenv import load_dotenv

# Load the .env file from the root directory
root_dir = r"C:\Users\tarun\Downloads\MiroFish-main (1)\MiroFish-main"
load_dotenv(os.path.join(root_dir, ".env"))

# Import our outreach engine
sys.path.append(os.path.join(root_dir, "mirofish_os", "monetization"))
from outreach_engine import AgencyOutreachEngine

async def run_test():
    print("Initializing Sparky Digital Services Agency...")
    agency = AgencyOutreachEngine()
    
    print("\nGenerating AI Pitch...")
    # Creating a dummy scenario for the test
    pitch_data = agency.generate_pitch(
        client_name="Test Business Owner", 
        business_type="E-commerce", 
        pain_point="spending too much time manually handling customer support emails"
    )
    
    print("\nPitch Data Ready:")
    print(f"Price Set: INR {pitch_data['price']}")
    print(f"Link Generated: {pitch_data['payment_link']}")
    
    print(f"\nSending Cold Email to sparkysolutions10@gmail.com...")
    success = await agency.send_cold_email("sparkysolutions10@gmail.com", pitch_data)
    
    if success:
        print("\n✅ TEST SUCCESSFUL! Email delivered.")
    else:
        print("\n❌ TEST FAILED! Check logs.")

if __name__ == "__main__":
    asyncio.run(run_test())
