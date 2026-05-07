import base64
import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from app.models.schemas import VisionAssessment

load_dotenv()

VISION_SYSTEM_PROMPT = """
You are a warranty inspection assistant. Extract structured findings from evidence.
Focus on: hardware damage, water exposure/corrosion, tampering, and image usability.
Do not speculate. Return STRICT JSON only.
"""

class ClaimsEvidenceAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
                            "text": "Analyze image. Return JSON: damage_type, severity, confidence, water_damage_visible, image_quality"
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
                        },
                    ],
                },
            ],
        )

        data = json.loads(response.choices[0].message.content)
        
        return VisionAssessment(
            damage_type=data.get("damage_type", "unknown"),
            severity=data.get("severity", "unknown"),
            confidence=data.get("confidence", 0.0),
            water_damage_visible=data.get("water_damage_visible", False),
            image_quality=data.get("image_quality", "poor")
        )
