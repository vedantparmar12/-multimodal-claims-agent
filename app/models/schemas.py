from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# This is our source of truth for claim data as it moves through the system
class ClaimWorkflowState(BaseModel):
    claim_id: str
    customer_statement: Optional[str] = None
    # We'll populate these during the RAG/Multimodal steps
    retrieved_clauses: List[dict] = Field(default_factory=list) 
    vision_assessment: Optional[dict] = None
    
    # Track what we still need from the user
    missing_requirements: List[str] = Field(default_factory=list)
    final_decision: Optional[dict] = None

class ClaimSession(BaseModel):
    claim_id: str
    status: Literal["open", "awaiting_documents", "under_review"]

class VisionAssessment(BaseModel):
    damage_type: str
    confidence: float
    water_damage_visible: bool
    image_quality: str

class UploadedEvidence(BaseModel):
    claim_id: str
    image_path: str