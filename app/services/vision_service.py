"""Vision Service — Image Analysis via Llama 4 Scout 17B (Multimodal)."""
import base64
from app.core.llm_client import get_groq_client
from app.core.config import settings


class VisionService:
    def __init__(self):
        self.client = get_groq_client()

    def analyze_sketch(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
        """
        Analyze an image/sketch using Llama 4 Scout 17B multimodal model.
        Returns a text description suitable for CAD parameter extraction.
        """
        # Encode image to base64 data URL
        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        image_data_url = f"data:{mime_type};base64,{b64_image}"

        analysis_prompt = (
            "Analisa gambar/sketsa teknis berikut. "
            "Identifikasi objek, dimensi yang terlihat, dan berikan "
            "deskripsi detail untuk keperluan pembuatan gambar CAD 2D "
            "(tampak atas dan tampak depan). "
            "Sebutkan tipe objek (meja, kursi, ruangan, dll), "
            "estimasi ukuran dalam cm, dan detail konstruksi."
        )

        try:
            completion = self.client.chat.completions.create(
                model=settings.VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": analysis_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_data_url
                                }
                            }
                        ]
                    }
                ],
                temperature=settings.DEFAULT_TEMPERATURE_VISION,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None
            )

            # Collect streaming chunks
            full_response = ""
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                full_response += content

            return full_response

        except Exception as e:
            print(f"Vision Error: {e}")
            return ""
