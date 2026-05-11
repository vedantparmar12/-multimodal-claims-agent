from app.models.schemas import ClaimWorkflowState
from app.claims_logic.engine import ClaimsDecisionEngine
from app.multimodal.analyzer import ClaimsEvidenceAnalyzer
from app.knowledge.store import PolicyStore

class ClaimWorkflow:
    def __init__(self):
        self.engine = ClaimsDecisionEngine()
        self.analyzer = ClaimsEvidenceAnalyzer()
        self.retriever = PolicyStore()

    def process_claim(self, state: ClaimWorkflowState, image_path: str) -> ClaimWorkflowState:
        # Pull policy context
        if state.customer_statement:
            state.retrieved_clauses = self.retriever.search(state.customer_statement)

        # Visual fact extraction
        state.vision_assessment = self.analyzer.analyze_damage_image(image_path)

        # Policy enforcement
        state.final_decision = self.engine.evaluate(state)
        
        return state
