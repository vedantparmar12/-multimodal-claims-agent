import os
from fastapi import APIRouter, HTTPException
from app.models.schemas import UploadedEvidence, ClaimWorkflowState
from app.agents.workflow import ClaimWorkflow

router = APIRouter()
workflow = ClaimWorkflow()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/claims/evaluate")
async def evaluate_claim(evidence: UploadedEvidence):
    if not os.path.exists(evidence.image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        state = ClaimWorkflowState(claim_id=evidence.claim_id)
        
        result = workflow.process_claim(state, evidence.image_path)
        
        return {
            "claim_id": result.claim_id,
            "assessment": result.vision_assessment,
            "decision": result.final_decision
        }
        
    except Exception as e:
        # Triage failure
        raise HTTPException(status_code=500, detail=str(e))
