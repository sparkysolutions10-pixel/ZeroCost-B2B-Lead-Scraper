
from pydantic_settings import BaseSettings, SettingsConfigDict


class OSSettings(BaseSettings):
    """
    Master Configuration for MiroFish Autonomous OS.
    Uses Pydantic v2 BaseSettings for environment variable parsing.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API Keys
    GROQ_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    
    # OpenRouter Unified Endpoint & Key
    LLM_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_API_KEY: str | None = None

    # Server Settings
    API_PORT: int = 8000
    WEBHOOK_PORT: int = 5055
    HOST: str = "0.0.0.0"

    # OS Paths
    WORKSPACE_DIR: str = "workspaces"
    QUARANTINE_DIR: str = "quarantine"
    DB_PATH: str = "mirofish_memory.db"

    # Hardware Tuning
    MAX_WORKERS: int = 8  # i5 8-core CPU
    MEMORY_LIMIT_GB: int = 16  # Dell 16GB RAM limit

    # Evolution & Shadow Sandbox
    SHADOW_SANDBOX_DIR: str = "shadow_sandbox"

    # Keystone & Paywall
    STRIPE_WEBHOOK_SECRET: str | None = None
    LEMONSQUEEZY_WEBHOOK_SECRET: str | None = None

settings = OSSettings()
