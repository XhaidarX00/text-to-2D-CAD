"""Audio Service — Speech to Text via Whisper Large v3 Turbo."""
from app.core.llm_client import get_groq_client
from app.core.config import settings


class AudioService:
    def __init__(self):
        self.client = get_groq_client()

    async def transcribe_audio(self, file_content: bytes, filename: str) -> dict:
        """
        Transcribe audio file to text using Whisper Large v3 Turbo.
        Returns dict with text, language, duration, and segments.
        """
        try:
            transcription = self.client.audio.transcriptions.create(
                file=(filename, file_content),
                model=settings.STT_MODEL,
                temperature=0,
                response_format="verbose_json",
            )

            return {
                "text": transcription.text,
                "language": getattr(transcription, "language", "id"),
                "duration": getattr(transcription, "duration", None),
                "segments": getattr(transcription, "segments", []),
            }

        except Exception as e:
            print(f"Whisper Error: {e}")
            return {
                "text": "",
                "language": "id",
                "duration": None,
                "segments": [],
            }
