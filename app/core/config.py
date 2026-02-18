import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Global application settings loaded from environment."""

    PROJECT_NAME = "AI CAD Architect"
    VERSION = "1.0.0"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OUTPUT_DIR: str = "outputs"

    # AI Model Configuration
    LLM_MODEL = "llama-3.3-70b-versatile"
    VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
    STT_MODEL = "whisper-large-v3-turbo"

    # Defaults
    MAX_IMAGE_SIZE_MB = 1
    DEFAULT_TEMPERATURE_LLM = 0.1
    DEFAULT_TEMPERATURE_VISION = 0.3


settings = Settings()
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
