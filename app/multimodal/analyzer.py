import base64
import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from app.models.schemas import VisionAssessment

load_dotenv()

VISION_SYSTEM_PROMPT = """
You are a warranty inspection assistant. Extract findings from hardware images.
IMPORTANT: Return STRICT JSON with these types:
- damage_type: string
- severity: string
- confidence: float (0.0 to 1.0)
- water_damage_visible: boolean
- image_quality: string
"""

class ClaimsEvidenceAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _safe_float(self, value, default=0.0):
        """Coerces potential string confidence labels to floats."""
        mapping = {"high": 0.9, "medium": 0.6, "low": 0.3}
        if isinstance(value, str):
            return mapping.get(value.lower(), default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def analyze_damage_image(self, image_path: str) -> VisionAssessment:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

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

        raw_data = json.loads(response.choices[0].message.content)
        
        return VisionAssessment(
            damage_type=raw_data.get("damage_type"),
            confidence=raw_data.get("confidence", 0.0),
            water_damage_visible=raw_data.get("water_damage_visible", False),
            tampering_visible=raw_data.get("tampering_visible", False),
            image_quality=raw_data.get("image_quality", "good")
        )

        data = json.loads(response.choices[0].message.content)
        
        # Apply normalization before creating the Pydantic model
        return VisionAssessment(
            damage_type=str(data.get("damage_type", "unknown")),
            severity=str(data.get("severity", "unknown")),
            confidence=self._safe_float(data.get("confidence")),
            water_damage_visible=bool(data.get("water_damage_visible", False)),
            image_quality=str(data.get("image_quality", "poor"))
        )
