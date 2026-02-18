"""Reasoning Service — Text to CAD Parameters via Llama 3.3 70B (streaming)."""
import json
from app.core.llm_client import get_groq_client
from app.core.config import settings


class ReasoningService:
    def __init__(self):
        self.client = get_groq_client()

    def extract_cad_parameters(self, user_prompt: str) -> dict:
        """
        Convert natural language description to JSON CAD parameters
        using Llama 3.3 70B with streaming response.
        """
        system_prompt = """
        Anda adalah Senior CAD Engineer. Tugas anda adalah mengekstrak parameter geometri dari input user.
        Output WAJIB JSON valid tanpa markdown.

        Schema JSON:
        {
            "shape_type": "box" | "cylinder" | "chair" | "room" | "l_shape",
            "width": float (default 100),
            "length": float (default 100),
            "height": float (default 50),
            "diameter": float (jika silinder, default null),
            "legs": int (jumlah kaki jika chair, default null),
            "doors": [{"wall": "north|south|east|west", "width": float}] (jika room, default null),
            "windows": [{"wall": "north|south|east|west", "width": float}] (jika room, default null),
            "description": "ringkasan singkat objek"
        }

        Aturan:
        - Konversi semua satuan ke CM (meter x 100).
        - Jika user tidak sebut ukuran, gunakan standar ergonomi furnitur.
        - Untuk kursi: width=40, length=40, height=45, legs=4.
        - Untuk meja: width=120, length=60, height=75.
        - Untuk ruangan: satuan biasanya meter, konversi ke cm.
        - shape_type HARUS salah satu dari: box, cylinder, chair, room, l_shape.
        """

        try:
            completion = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_prompt
                            }
                        ]
                    }
                ],
                temperature=settings.DEFAULT_TEMPERATURE_LLM,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
                response_format={"type": "json_object"}
            )

            # Collect streaming chunks into full response
            full_response = ""
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                full_response += content

            return json.loads(full_response)

        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}, raw: {full_response[:200]}")
            return self._fallback_params()
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._fallback_params()

    @staticmethod
    def _fallback_params() -> dict:
        """Return safe default parameters when LLM fails."""
        return {
            "shape_type": "box",
            "width": 100,
            "length": 100,
            "height": 50,
            "description": "Default box (LLM fallback)"
        }
