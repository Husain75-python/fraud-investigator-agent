# 🛡️ TigerGraph Agentic Fraud Investigation System

An end-to-end, multi-agent AI fraud investigation platform built for the **Agentic Fraud Investigation Hackathon**. The system combines **TigerGraph Savanna (MCP)** for multi-hop graph topology traversals, **Vector GraphRAG** for bank compliance policy grounding, **LangGraph** for stateful decision orchestration, and **Groq** for high-speed, cost-effective LLM reasoning.

---

## 🌟 Key Features

* **🕸️ Multi-Hop Topology Retrieval (TigerGraph MCP):** Dynamically queries target transactions, connected accounts, shared devices, and IP addresses using GSQL interpret queries on TigerGraph Savanna cloud platform.
* **📜 Compliance Policy GraphRAG:** Vector-searches bank policy guidelines (e.g., \POL-101\, \POL-103\) to ensure every automated action or recommendation is legally defensible and grounded.
* **🔀 Stateful Multi-Agent Workflow (LangGraph):** Evaluates transaction risk alongside uncertainty scores. Automatically triggers step-up verification for ambiguous edge cases or escalates high-risk cases directly to account block.
* **✍️ Persistent Memory Loop:** Automatically writes case outcomes, risk decisions, and SAR flags back into TigerGraph as \FraudCase\ vertices linked via \LINKED_TO_CASE\ edges.
* **⚡ High-Speed Inference (Groq):** Powered by open-source LLMs (\openai/gpt-oss-120b\) via Groq API for rapid evaluation without quota limits.
* **📊 Benchmark Evaluator & Streamlit Dashboard:** Complete test harness evaluating 20 benchmark cases automatically alongside an interactive UI for case exploration and network topology visualization.

---

## 🏗️ System Architecture

\\\
[ Incoming Transaction ]
         │
         ▼
[ Node 1: TigerGraph MCP Tool ] ──(2-Hop Traversal)──► TigerGraph Savanna Cloud
         │
         ▼
[ Node 2: Policy GraphRAG ] ──────(Vector Search)────► Chroma Vector Store
         │
         ▼
[ Node 3: Risk & Uncertainty Assessor ]
         │
         ├─── (0.35 <= Risk <= 0.75) ──► [ Node 4: Step-Up Auth Simulation ]
         │                                               │
         ▼                                               ▼
[ Node 5: Next-Best Action Engine ] ◄────────────────────┘
         │
         ├─── Generates SAR Report (if sar_required = true)
         │
         ▼
[ Node 6: Persistent Graph Memory ] ──(Upsert Vertex/Edge)──► TigerGraph Savanna
\\\

---

## 📁 Repository Structure

\\\
fraud-investigator-agent/
│
├── data/
│   ├── benchmark/            # 20 JSON test cases for evaluation
│   ├── policy/               # Compliance policy documents for GraphRAG
│   └── raw/                  # Raw transaction schemas and CSVs
│
├── outputs/
│   ├── benchmark_results/    # Generated submission answer JSONs (output_case_*.json)
│   └── sars/                 # Filed Suspicious Activity Report (SAR) text narratives
│
├── src/
│   ├── agent/
│   │   ├── nodes.py          # LangGraph node logic and reasoning prompts
│   │   ├── state.py          # FraudInvestigationState typed dictionary
│   │   └── workflow.py       # LangGraph state machine edge & route graph
│   │
│   ├── tools/
│   │   ├── policy_rag.py     # Vector policy retrieval engine
│   │   └── tg_mcp.py         # TigerGraph MCP connection & GSQL executor
│   │
│   └── utils/
│       └── benchmark_runner.py # Evaluation harness for processing all test cases
│
├── .env.example              # Environment variable template
├── app.py                    # Streamlit interactive dashboard
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
\\\

---

## ⚙️ Installation & Setup

### 1. Prerequisites
* **Python:** 3.10 or higher
* **TigerGraph Savanna Account:** Instance configured with \Transaction_Fraud\ graph schema
* **Groq API Key:** Free key from [console.groq.com](https://console.groq.com/keys)

### 2. Environment Setup

Clone the repository and set up a virtual environment:

\\\ash
git clone https://github.com/your-username/fraud-investigator-agent.git
cd fraud-investigator-agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
\\\

### 3. Configure Environment Variables

Create a \.env\ file in the project root based on \.env.example\:

\\\env
# LLM Provider Configuration
LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-120b
GROQ_API_KEY=your_groq_api_key_here

# TigerGraph Savanna Credentials
TG_HOST=https://savanna.tgcloud.io
TG_GRAPH_NAME=Transaction_Fraud
TG_USERNAME=your_email@domain.com
TG_SECRET=your_tigergraph_secret_here
\\\

---

## 🚀 Running the System

### 1. Run Batch Benchmark Evaluation (20 Cases)

To evaluate the agent against all 20 benchmark test cases and generate official output answer files:

\\\ash
python -m src.utils.benchmark_runner
\\\

**Outputs generated:**
* Final answer JSONs saved in \outputs/benchmark_results/\
* Suspicious Activity Reports saved in \outputs/sars/\

### 2. Launch Streamlit Interactive Dashboard

To launch the web dashboard for interactive case investigation, visualization, and memory state inspection:

\\\ash
streamlit run app.py
\\\

Navigating the Streamlit App:
1. **Interactive Case Investigator:** Interactively run target transaction IDs, simulate step-up verifications, and view connected 2-hop topology networks.
2. **Batch Benchmark Evaluator:** Inspect generated \output_case_*.json\ submission answer files.
3. **Memory & Graph State:** Verify write-back feedback loops committed into TigerGraph Savanna.

---

## 🏆 Benchmark & Evaluation Highlights

* **Precision:** Accurately routes transactions using initial risk scores, graph pattern detection (\SHARED_DEVICE_MULTI_ACCOUNT\), and policy threshold matching.
* **Auditable Reasoning:** Every recommendation outputs structured JSON citing specific bank policies (\POL-101\, \POL-103\).
* **Automated SAR Generation:** Automatically drafts full narrative Suspicious Activity Reports for transactions exceeding risk thresholds.

---

## 📜 License

This project is licensed under the MIT License - see the \LICENSE\ file for details.
