from app.models.schemas import ClaimWorkflowState, ClaimDecision

class ClaimsWorkflow:
    def initialize_claim(self, claim_id: str, customer_statement: str) -> ClaimWorkflowState:
        # Starting with a hardcoded list of requirements for the MVP.
        # In a production system, these would be dynamic based on the issue type.
        return ClaimWorkflowState(
            claim_id=claim_id,
            customer_statement=customer_statement,
            missing_requirements=[
                "damage_image",
                "proof_of_purchase",
                "serial_number_image",
            ],
        )

    def evaluate_stub(self, state: ClaimWorkflowState) -> ClaimWorkflowState:
        # Initial triage stub to ensure the API wiring is functional.
        # We'll replace this with real RAG + Multimodal logic in Task 2/3.
        state.final_decision = ClaimDecision(
            decision="manual_review",
            reason_codes=["INITIAL_TRIAGE_PENDING"],
            confidence=0.35
        )
        return state
