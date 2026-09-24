from typing import TypedDict, List, Dict, Optional, Any

class FraudInvestigationState(TypedDict):
    # Incident Details
    case_id: str
    transaction_id: str
    customer_id: str
    initial_risk_score: float
    
    # Evidence & Traversal Data
    graph_topology: Dict[str, Any]
    matched_patterns: List[str]
    retrieved_policies: List[str]
    similar_past_cases: List[Dict[str, Any]]
    
    # Risk Assessment & Controls
    uncertainty_score: float  # Scale 0.0 (certain) to 1.0 (uncertain)
    evidence_requested: bool
    additional_evidence: Optional[Dict[str, Any]]
    
    # Decisions & Actions
    pre_evidence_action: Optional[str]
    recommended_action: str  # ALLOW, BLOCK, STEP_UP_AUTH, ESCALATE
    approval_required: bool
    action_executed: bool
    
    # Final Output Deliverables
    explanation_reasoning: str
    sar_required: bool
    sar_report: Optional[str]