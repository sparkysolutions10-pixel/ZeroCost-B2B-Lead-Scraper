import os
import glob
import logging

logger = logging.getLogger("mirofish.agents")

class AgencyAgentLoader:
    """
    Customized loader for msitarzewski/agency-agents.
    Reads the markdown personas and turns them into system prompts for MiroFish workers.
    """
    def __init__(self, agents_dir: str = "agency-agents"):
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.agents_dir = os.path.join(base_path, agents_dir)
        self.personas = {}
        self._load_agents()

    def _load_agents(self):
        if not os.path.exists(self.agents_dir):
            logger.warning(f"Agency agents directory not found at {self.agents_dir}")
            return
            
        # Search for markdown files in the repo (assuming they are in roles/ or root)
        md_files = glob.glob(f"{self.agents_dir}/**/*.md", recursive=True)
        for file_path in md_files:
            if "README" in file_path.upper():
                continue
                
            agent_name = os.path.basename(file_path).replace(".md", "")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Store the persona prompt
            self.personas[agent_name.lower()] = content
            
        logger.info(f"Successfully loaded {len(self.personas)} autonomous agents into MiroFish OS.")

    def get_agent_prompt(self, role_name: str) -> str:
        """Fetch the system prompt for a specific agent role."""
        return self.personas.get(role_name.lower(), "You are a helpful AI assistant.")

# Singleton instance
agency_team = AgencyAgentLoader()
