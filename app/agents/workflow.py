from app.models.schemas import ClaimWorkflowState
from app.claims_logic.engine import ClaimsDecisionEngine
from app.multimodal.analyzer import ClaimsEvidenceAnalyzer

class ClaimWorkflow:
    def __init__(self):
        self.engine = ClaimsDecisionEngine()
        self.analyzer = ClaimsEvidenceAnalyzer()

    def process_claim(self, state: ClaimWorkflowState, image_path: str) -> ClaimWorkflowState:
        # 1. Vision extraction
        state.vision_assessment = self.analyzer.analyze_damage_image(image_path)
        
        # 2. Deterministic policy check
        state.final_decision = self.engine.evaluate(state)
        
        return state
