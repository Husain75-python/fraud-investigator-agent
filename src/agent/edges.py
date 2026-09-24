from src.agent.state import FraudInvestigationState
from src.utils.config import config

def evaluate_uncertainty_gate(state: FraudInvestigationState) -> str:
    """
    Evaluates risk and uncertainty to route the investigation flow:
    1. If uncertainty is high (> 0.4) and additional evidence hasn't been requested yet -> Request Evidence.
    2. If human approval is strictly required by policy -> Escalate to Analyst.
    3. Otherwise -> Execute Next Best Action directly.
    """
    uncertainty = state.get("uncertainty_score", 1.0)
    evidence_already_requested = state.get("evidence_requested", False)
    
    # High uncertainty trigger -> Loop to gather step-up evidence
    if uncertainty >= 0.40 and not evidence_already_requested:
        return "request_evidence"
    
    # Explicit policy route requiring human override
    if state.get("approval_required", False):
        return "escalate_to_human"
        
    return "execute_action"


def check_approval_requirement(state: FraudInvestigationState) -> str:
    """
    Determines if an action can be executed automatically or requires human analyst intervention.
    """
    action = state.get("recommended_action", "ALLOW")
    risk = state.get("initial_risk_score", 0.0)

    # Policy rule: High-value blocks or account freezes require analyst approval route
    if action in ["BLOCK", "FREEZE_ACCOUNT"] and risk < config.HIGH_RISK_THRESHOLD:
        state["approval_required"] = True
        return "require_analyst_signoff"
    
    return "proceed_automation"