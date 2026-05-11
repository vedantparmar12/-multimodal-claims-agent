import os
from fastapi import APIRouter, HTTPException
from app.models.schemas import ClaimWorkflowState, ClaimRequest
from app.agents.workflow import ClaimWorkflow

router = APIRouter()
workflow = ClaimWorkflow()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/claims/evaluate")
async def evaluate_claim(request: ClaimRequest):
    evidence = request.evidence

    if not os.path.exists(evidence.image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        # Initialize state with the user's input
        state = ClaimWorkflowState(
            claim_id=evidence.claim_id,
            customer_statement=request.customer_statement
        )

        result = workflow.process_claim(state, evidence.image_path)

        clean_policy_context = [
            clause for clause in result.retrieved_clauses
            if clause['relevance_score'] > 0.22 and "Project:" not in clause['content']
        ]

        return {
            "claim_id": result.claim_id,
            "assessment": result.vision_assessment,
            "decision": result.final_decision,
            "policy_context": clean_policy_context
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
