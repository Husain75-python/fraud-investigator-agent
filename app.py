import streamlit as st
import json
import pandas as pd
from pathlib import Path
from src.agent.workflow import fraud_agent
from src.utils.benchmark_runner import run_benchmark

st.set_page_config(
    page_title="TigerGraph Agentic Fraud Investigator",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ TigerGraph Agentic Fraud Investigation System")
st.caption("Powered by TigerGraph MCP, GraphRAG, and LangGraph Multi-Agent Orchestration")

tabs = st.tabs(["🔍 Interactive Case Investigator", "📊 Batch Benchmark Evaluator (20 Cases)", "📜 Memory & Graph State"])

# TAB 1: Live Single Case Investigator
with tabs[0]:
    st.subheader("Investigate Transaction Case")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        tx_id = st.text_input("Transaction ID", value="TX_1002")
    with col2:
        cust_id = st.text_input("Customer ID", value="CUST_1082")
    with col3:
        risk_score = st.slider("Model Fraud Score", min_value=0.0, max_value=1.0, value=0.68, step=0.01)

    if st.button("🚀 Run Agent Investigation", type="primary"):
        with st.spinner("Agent analyzing TigerGraph topology, policies, and uncertainty..."):
            initial_state = {
                "case_id": f"CASE_LIVE_{tx_id}",
                "transaction_id": tx_id,
                "customer_id": cust_id,
                "initial_risk_score": risk_score,
                "uncertainty_score": 1.0,
                "evidence_requested": False,
                "action_executed": False
            }
            
            res = fraud_agent.invoke(initial_state)

        st.success("Investigation Completed!")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Recommended Action", res["recommended_action"])
        m2.metric("Pre-Evidence Action", res.get("pre_evidence_action", "N/A"))
        m3.metric("Uncertainty Score", f"{res['uncertainty_score']:.2f}")
        m4.metric("SAR Required", "YES ⚠️" if res.get("sar_required") else "NO ✅")

        st.divider()

        left_col, right_col = st.columns(2)
        
        with left_col:
            st.write("### 🕸️ Graph Evidence Topology (TigerGraph)")
            st.json(res.get("graph_topology", {}))
            
            st.write("### 📖 Policy GraphRAG Grounding")
            for pol in res.get("retrieved_policies", []):
                st.info(pol)

        with right_col:
            st.write("### 🧠 Agent Explanation & Reasoning")
            st.write(res.get("explanation_reasoning", "No explanation generated."))
            
            if res.get("sar_required") and res.get("sar_report"):
                st.write("### 📄 Generated Suspicious Activity Report (SAR)")
                st.text_area("SAR Text", value=res["sar_report"], height=200)

# TAB 2: Batch Benchmark Evaluator
with tabs[1]:
    st.subheader("Run Agent on 20 Benchmark Evaluation Cases")
    st.write("This tool processes the benchmark test set and produces the submission answer files in `outputs/benchmark_results/`.")
    
    if st.button("⚡ Execute All 20 Benchmark Cases", type="primary"):
        with st.spinner("Processing benchmark suite..."):
            run_benchmark()
        st.success("Batch evaluation complete! Outputs generated in outputs/benchmark_results/")

    results_dir = Path("outputs/benchmark_results")
    if results_dir.exists():
        files = sorted(list(results_dir.glob("*.json")))
        if files:
            st.write(f"#### Generated Results ({len(files)} files)")
            selected_file = st.selectbox("Select Case Result File", options=[f.name for f in files])
            if selected_file:
                with open(results_dir / selected_file, "r") as f:
                    data = json.load(f)
                st.json(data)

# TAB 3: Memory & State View
with tabs[2]:
    st.subheader("Persistent Graph Memory Logs")
    st.write("Displays cases committed back to TigerGraph for long-term pattern analysis.")
    st.info("Vertices written: `FraudCase` linked to `Transaction` via `LINKED_TO_CASE` edge.")