from groq import Groq
from app.core.config import settings

# Singleton Groq Client
_client = None


def get_groq_client() -> Groq:
    """Return a singleton Groq client instance."""
    global _client
    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client
