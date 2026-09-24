import json
import os
import re
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from src.agent.state import FraudInvestigationState
from src.tools.tg_mcp import TigerGraphMCPTool
from src.tools.policy_rag import PolicyRAG

load_dotenv()

# Select provider dynamically: 'groq' or 'openai'
provider = os.getenv("LLM_PROVIDER", "groq").lower()

if provider == "groq":
    from langchain_groq import ChatGroq
    model_name = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
    llm = ChatGroq(model=model_name, temperature=0.0)
else:
    from langchain_openai import ChatOpenAI
    model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=model_name, temperature=0.0)

tg_mcp = TigerGraphMCPTool()
policy_rag = PolicyRAG()

def gather_graph_evidence(state: FraudInvestigationState) -> FraudInvestigationState:
    """Node 1: Pulls 2-hop connected graph topology and historical case memory."""
    topology = tg_mcp.get_transaction_topology(state["transaction_id"])
    past_cases = tg_mcp.query_similar_cases(state["customer_id"])
    
    if not isinstance(topology, dict):
        topology = {"customer_id": state["customer_id"], "devices": [], "ips": []}

    state["graph_topology"] = topology
    state["similar_past_cases"] = past_cases
    
    devices = topology.get("devices", []) if isinstance(topology, dict) else []
    state["matched_patterns"] = ["SHARED_DEVICE_MULTI_ACCOUNT"] if len(devices) > 0 else []
    return state

def search_policy_rag(state: FraudInvestigationState) -> FraudInvestigationState:
    """Node 2: Queries bank policy guidelines using vector GraphRAG."""
    query = f"Risk score {state['initial_risk_score']} with pattern {state['matched_patterns']}"
    policies = policy_rag.search_policies(query)
    state["retrieved_policies"] = policies
    return state

def assess_risk_and_uncertainty(state: FraudInvestigationState) -> FraudInvestigationState:
    """Node 3: Calculates uncertainty level and determines initial/final actions."""
    score = state["initial_risk_score"]
    
    # Calculate uncertainty: mid-tier scores trigger step-up verification request
    if 0.35 <= score <= 0.75 and not state.get("evidence_requested", False):
        state["uncertainty_score"] = 0.8
        state["pre_evidence_action"] = "REQUEST_STEP_UP_AUTH"
    else:
        state["uncertainty_score"] = 0.1
        state["pre_evidence_action"] = state.get("pre_evidence_action", "BLOCK" if score > 0.75 else "ALLOW")

    return state

def request_additional_evidence(state: FraudInvestigationState) -> FraudInvestigationState:
    """Node 4: Controlled action to simulate Step-Up Authentication / Customer Validation."""
    state["evidence_requested"] = True
    state["additional_evidence"] = {"step_up_auth_passed": False, "validation_timestamp": "2026-09-24T12:00:00Z"}
    state["initial_risk_score"] = 0.90  # Escalate risk score post-failed verification
    return state

def execute_next_best_action(state: FraudInvestigationState) -> FraudInvestigationState:
    """Node 5: Formulates defensible recommendation and generates SAR if required."""
    prompt = f"""
    You are an AI Fraud Analyst. Synthesize the evidence and select the next best action:
    - Customer ID: {state['customer_id']}
    - Risk Score: {state['initial_risk_score']}
    - Topology Evidence: {json.dumps(state['graph_topology'])}
    - Policies: {json.dumps(state['retrieved_policies'])}
    - Additional Evidence: {json.dumps(state.get('additional_evidence', {}))}

    Output JSON format only:
    {{
      "recommended_action": "BLOCK | ALLOW | STEP_UP_AUTH | ESCALATE",
      "sar_required": true,
      "explanation_reasoning": "Clear explanation citing evidence and policies.",
      "sar_report": "Detailed SAR narrative if sar_required is true, else null"
    }}
    """
    response = llm.invoke([
        SystemMessage(content="Return strictly valid JSON. Do not wrap output in markdown syntax."),
        HumanMessage(content=prompt)
    ])
    
    # Ensure text content extraction is string-safe
    raw_text = response.content if isinstance(response.content, str) else str(response.content)
    
    # Clean output from potential markdown formatting blocks like ```json ... ``` and replace non-breaking hyphens
    cleaned_content = re.sub(r"```(?:json)?\n?|\n?```", "", raw_text.strip())
    cleaned_content = cleaned_content.replace("\u2011", "-")
    
    try:
        res = json.loads(cleaned_content)
    except json.JSONDecodeError:
        res = {
            "recommended_action": "BLOCK" if state['initial_risk_score'] > 0.75 else "ALLOW",
            "sar_required": state['initial_risk_score'] > 0.75,
            "explanation_reasoning": "Fallback decision executed due to JSON parsing format.",
            "sar_report": None
        }

    state["recommended_action"] = res.get("recommended_action", "BLOCK")
    state["sar_required"] = res.get("sar_required", False)
    
    # Sanitize reasoning string for Windows console and file writing safety
    reasoning = res.get("explanation_reasoning", "Action processed.")
    if isinstance(reasoning, str):
        reasoning = reasoning.replace("\u2011", "-")
        
    sar_rep = res.get("sar_report")
    if isinstance(sar_rep, str):
        sar_rep = sar_rep.replace("\u2011", "-")

    state["explanation_reasoning"] = reasoning
    state["sar_report"] = sar_rep
    return state

def write_to_case_memory(state: FraudInvestigationState) -> FraudInvestigationState:
    """Node 6: Writes resolution back to TigerGraph for persistent memory."""
    tg_mcp.write_case_to_graph(
        case_id=state["case_id"],
        tx_id=state["transaction_id"],
        status="CLOSED",
        decision=state["recommended_action"],
        sar_filed=state["sar_required"]
    )
    state["action_executed"] = True
    return state