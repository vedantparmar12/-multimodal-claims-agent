import base64
import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ClaimsEvidenceAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def analyze_damage(self, image_path: str):
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system", 
                    "content": "Analyze hardware damage. Return JSON: damage_type (str), severity (low/med/high), confidence (float 0-1), water_damage (bool)."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract damage findings from this claim evidence image."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                    ],
                },
            ],
        )
        return json.loads(response.choices[0].message.content)
