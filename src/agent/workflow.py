from langgraph.graph import StateGraph, START, END
from src.agent.state import FraudInvestigationState
from src.agent.nodes import (
    gather_graph_evidence,
    search_policy_rag,
    assess_risk_and_uncertainty,
    request_additional_evidence,
    execute_next_best_action,
    write_to_case_memory
)

def evaluate_uncertainty_gate(state: FraudInvestigationState) -> str:
    """Routes to evidence gathering if uncertainty is high and evidence hasn't been requested yet."""
    if state["uncertainty_score"] > 0.4 and not state.get("evidence_requested", False):
        return "request_evidence"
    return "execute_action"

# Initialize Graph
builder = StateGraph(FraudInvestigationState)

# Add Nodes
builder.add_node("gather_evidence", gather_graph_evidence)
builder.add_node("search_policy", search_policy_rag)
builder.add_node("assess_risk", assess_risk_and_uncertainty)
builder.add_node("request_evidence", request_additional_evidence)
builder.add_node("execute_action", execute_next_best_action)
builder.add_node("commit_memory", write_to_case_memory)

# Flow Connections
builder.add_edge(START, "gather_evidence")
builder.add_edge("gather_evidence", "search_policy")
builder.add_edge("search_policy", "assess_risk")

builder.add_conditional_edges(
    "assess_risk",
    evaluate_uncertainty_gate,
    {
        "request_evidence": "request_evidence",
        "execute_action": "execute_action"
    }
)

builder.add_edge("request_evidence", "assess_risk")
builder.add_edge("execute_action", "commit_memory")
builder.add_edge("commit_memory", END)

fraud_agent = builder.compile()