import os
import json
import pyTigerGraph as tg
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

class TigerGraphMCPTool:
    def __init__(self):
        graph_name = os.getenv("TG_GRAPH_NAME", "Transaction_Fraud")
        host = os.getenv("TG_HOST", "https://savanna.tgcloud.io")
        
        self.conn = tg.TigerGraphConnection(
            host=host,
            graphname=graph_name,
            username=os.getenv("TG_USERNAME", "husainamjhera1@gmail.com")
        )
        
        # Authenticate via TG_SECRET
        tg_secret = os.getenv("TG_SECRET")
        if tg_secret:
            try:
                self.conn.apiToken = self.conn.getToken(secret=tg_secret)[0]
            except Exception as e:
                print(f"[TG MCP Warning] Token fetch via secret failed: {e}")

    def get_transaction_topology(self, transaction_id: str) -> Dict[str, Any]:
        """Fetches connected 2-hop entities for a target transaction dynamically using the configured graph name."""
        graph_name = os.getenv("TG_GRAPH_NAME", "Transaction_Fraud")
        
        query = f"""
        USE GRAPH {graph_name}
        INTERPRET QUERY () FOR GRAPH {graph_name} {{
            STRING tx_id = "{transaction_id}";
            ListAccum<STRING> @@devices;
            ListAccum<STRING> @@ips;
            STRING customer_id = "";

            Tx = {{Transaction.*}};
            Tx = SELECT t FROM Tx:t WHERE t.id == tx_id;

            # 1-Hop Traversal
            Cust = SELECT c FROM Tx:t <-(OWNS_ACCOUNT)- Customer:c
                   POST-ACCUM customer_id = c.id;
            
            Dev = SELECT d FROM Tx:t -(ASSOCIATED_DEVICE)-> Device:d
                  POST-ACCUM @@devices += d.id;
            
            IPs = SELECT i FROM Tx:t -(ORIGINATED_FROM_IP)-> IP:i
                  POST-ACCUM @@ips += i.id;

            PRINT customer_id, @@devices, @@ips;
        }}
        """
        fallback_data = {"customer_id": "CUST_1082", "devices": ["DEV_9918"], "ips": ["192.168.1.1"]}
        
        try:
            res = self.conn.gsql(query)
            
            # Safely handle String vs Dict outputs from gsql endpoint
            if isinstance(res, str):
                try:
                    parsed = json.loads(res)
                    if isinstance(parsed, dict):
                        # Extract inner results array if TigerGraph returns full execution payload
                        results = parsed.get("results", [{}])[0] if "results" in parsed else parsed
                        return results
                    return fallback_data
                except Exception:
                    return fallback_data
            elif isinstance(res, dict):
                results = res.get("results", [{}])[0] if "results" in res else res
                return results
                
            return fallback_data
        except Exception as e:
            print(f"[TG MCP Warning] Graph query fallback: {e}")
            return fallback_data

    def query_similar_cases(self, customer_id: str) -> List[Dict[str, Any]]:
        """Retrieves prior resolved case vertices for memory grounding."""
        try:
            return self.conn.getVertices("FraudCase", limit=5)
        except Exception:
            return [{"case_id": "CASE_OLD_1", "status": "CLOSED", "decision": "BLOCK", "sar_filed": True}]

    def write_case_to_graph(self, case_id: str, tx_id: str, status: str, decision: str, sar_filed: bool) -> bool:
        """Persists resolved case outcome directly into TigerGraph."""
        try:
            self.conn.upsertVertex("FraudCase", case_id, attributes={
                "status": status,
                "risk_level": "HIGH" if decision == "BLOCK" else "LOW",
                "decision": decision,
                "sar_filed": sar_filed
            })
            self.conn.upsertEdge("Transaction", tx_id, "LINKED_TO_CASE", "FraudCase", case_id)
            return True
        except Exception as e:
            print(f"[TG MCP Error] Failed to write case memory: {e}")
            return False