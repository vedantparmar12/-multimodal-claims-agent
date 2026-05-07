# app/multimodal/prompts.py

DAMAGE_EXTRACTION_PROMPT = """
Analyze the provided hardware image for warranty claim validation. 
Refer to the VoltEdge Policy for specific exclusions.

Extract the following in structured JSON:
1. damage_type: (e.g., 'cracked_screen', 'frayed_cable')
2. water_damage_visible: Boolean. Look for corrosion, water spots, or submersion signs (VOID_ENVIRONMENTAL_ABUSE).
3. tampering_visible: Boolean. Look for broken warranty seals, mismatched screws, or pry marks (VOID_TAMPERING).
4. image_quality: 'good' if details are clear, 'poor' if blurry or dark.
5. confidence: Float (0.0 - 1.0) based on how certain you are of the damage assessment.

Only return the JSON object.
"""
