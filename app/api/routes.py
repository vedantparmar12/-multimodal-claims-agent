from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models.schemas import ClaimWorkflowState
from app.agents.workflow import ClaimWorkflow

router = APIRouter()
_workflow: ClaimWorkflow | None = None

def get_workflow() -> ClaimWorkflow:
    global _workflow
    if _workflow is None:
        _workflow = ClaimWorkflow()
    return _workflow

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/claims/evaluate")
async def evaluate_claim(
    claim_id: str = Form(...),
    customer_statement: str = Form(...),
    image: UploadFile = File(...)
):
    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Image file is empty")

    try:
        state = ClaimWorkflowState(
            claim_id=claim_id,
            customer_statement=customer_statement
        )
        result = get_workflow().process_claim(state, image_bytes)

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
