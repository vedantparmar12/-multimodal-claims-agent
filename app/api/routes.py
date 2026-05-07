import os
from fastapi import APIRouter, HTTPException
from app.models.schemas import UploadedEvidence
from app.multimodal.analyzer import ClaimsEvidenceAnalyzer

router = APIRouter()
analyzer = ClaimsEvidenceAnalyzer()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/analyze-image")
async def analyze_image(req: UploadedEvidence):
    """
    Triggers multimodal analysis on uploaded evidence.
    """
    if not os.path.exists(req.image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    
    try:
        return analyzer.analyze_damage(req.image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
