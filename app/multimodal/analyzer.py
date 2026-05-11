import base64
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from app.models.schemas import VisionAssessment

load_dotenv()

VISION_SYSTEM_PROMPT = """
You are a warranty inspection assistant. Extract findings from hardware images.
IMPORTANT: Return STRICT JSON with these types:
- damage_type: string
- confidence: float (0.0 to 1.0)
- water_damage_visible: boolean
- tampering_visible: boolean
- image_quality: string
"""

class ClaimsEvidenceAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _safe_float(self, value, default=0.0) -> float:
        mapping = {"high": 0.9, "medium": 0.6, "low": 0.3}
        if isinstance(value, str):
            return mapping.get(value.lower(), default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def analyze_damage_image(self, image_bytes: bytes) -> VisionAssessment:
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": VISION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "Analyze hardware for damage. Detect tampering and water exposure per policy."
                        },
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                    ],
                },
            ],
        )

        data = json.loads(response.choices[0].message.content)
        
        quality_map = {
            "excellent": "good", "high": "good", "good": "good", "medium": "good",
            "low": "poor", "poor": "poor", "blurry": "poor", "invalid": "invalid"
        }
        raw_quality = str(data.get("image_quality", "good")).lower()
        normalized_quality = quality_map.get(raw_quality, "good")

        damage = str(data.get("damage_type", "unknown"))
        conf = self._safe_float(data.get("confidence", 0.0))

        if any(word in damage.lower() for word in ["burn", "fire", "smoke"]):
            conf = 0.5 

        return VisionAssessment(
            damage_type=damage,
            confidence=conf,
            water_damage_visible=bool(data.get("water_damage_visible", False)),
            tampering_visible=bool(data.get("tampering_visible", False)),
            image_quality=normalized_quality
        )
