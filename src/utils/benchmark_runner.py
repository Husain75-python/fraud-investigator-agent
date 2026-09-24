import os
import json
import glob
from pathlib import Path
from src.agent.workflow import fraud_agent
import sys
import io

# Force stdout to output UTF-8 text on Windows consoles
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BENCHMARK_DIR = Path("data/benchmark")
OUTPUT_DIR = Path("outputs/benchmark_results")
SAR_DIR = Path("outputs/sars")

def load_mock_benchmark_cases():
    """Generates 20 benchmark case templates if data/benchmark directory is empty."""
    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
    existing_files = list(BENCHMARK_DIR.glob("case_*.json"))
    
    if len(existing_files) == 0:
        print("[Benchmark Setup] Generating initial 20 benchmark case configurations...")
        for i in range(1, 21):
            sample_case = {
                "case_id": f"CASE_BENCHMARK_{i:02d}",
                "transaction_id": f"TX_{1000 + i}",
                "customer_id": f"CUST_{200 + (i % 5)}",
                "risk_score": round(0.20 + (i * 0.038), 2)  # Varied risk scores across 20 cases
            }
            with open(BENCHMARK_DIR / f"case_{i:02d}.json", "w", encoding="utf-8") as f:
                json.dump(sample_case, f, indent=2, ensure_ascii=False)

def run_benchmark():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SAR_DIR.mkdir(parents=True, exist_ok=True)
    
    load_mock_benchmark_cases()
    case_files = sorted(list(BENCHMARK_DIR.glob("case_*.json")))
    print(f"\n🚀 Running Agent Evaluation on {len(case_files)} Benchmark Cases...\n")
    
    for case_file in case_files:
        with open(case_file, "r", encoding="utf-8") as f:
            case_input = json.load(f)
            
        initial_state = {
            "case_id": case_input["case_id"],
            "transaction_id": case_input["transaction_id"],
            "customer_id": case_input["customer_id"],
            "initial_risk_score": case_input["risk_score"],
            "uncertainty_score": 1.0,
            "evidence_requested": False,
            "action_executed": False
        }
        
        print(f"--> Processing Case: {case_input['case_id']} (Tx: {case_input['transaction_id']}, Initial Risk: {case_input['risk_score']})")
        
        # Execute Agentic Graph
        final_state = fraud_agent.invoke(initial_state)
        
        # Format official submission answer file
        output_payload = {
            "case_id": final_state["case_id"],
            "transaction_id": final_state["transaction_id"],
            "customer_id": final_state["customer_id"],
            "initial_risk_score": final_state["initial_risk_score"],
            "pre_evidence_action": final_state.get("pre_evidence_action"),
            "post_evidence_action": final_state["recommended_action"],
            "approval_route": "AUTOMATED_POLICY" if final_state["uncertainty_score"] < 0.5 else "ANALYST_APPROVAL_REQUIRED",
            "findings_and_evidence": {
                "topology": final_state.get("graph_topology", {}),
                "matched_patterns": final_state.get("matched_patterns", []),
                "policies_retrieved": final_state.get("retrieved_policies", [])
            },
            "reasoning_explanation": final_state.get("explanation_reasoning", ""),
            "sar_required": final_state.get("sar_required", False)
        }
        
        # Save output answer JSON with explicit utf-8 encoding
        out_path = OUTPUT_DIR / f"output_{case_file.name}"
        with open(out_path, "w", encoding="utf-8") as out_f:
            json.dump(output_payload, out_f, indent=2, ensure_ascii=False)
            
        # Save SAR text file if generated
        if final_state.get("sar_required") and final_state.get("sar_report"):
            sar_path = SAR_DIR / f"sar_{case_input['case_id']}.txt"
            with open(sar_path, "w", encoding="utf-8") as sar_f:
                sar_f.write(str(final_state["sar_report"]))
                
        print(f"    Verdict: {final_state['recommended_action']} | SAR Filed: {final_state.get('sar_required')} | Saved: {out_path.name}")

    print(f"\n✅ All 20 Benchmark Cases Successfully Processed and Output Files Saved to `{OUTPUT_DIR}`!\n")

if __name__ == "__main__":
    run_benchmark()