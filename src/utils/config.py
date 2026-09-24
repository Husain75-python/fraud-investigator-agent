import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    # LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
    TEMPERATURE: float = 0.0

    # TigerGraph Credentials
    TG_HOST: str = os.getenv("TG_HOST", "https://savanna.tgcloud.io")
    TG_USERNAME: str = os.getenv("TG_USERNAME", "husainamjhera1@gmail.com")
    TG_GRAPH_NAME: str = os.getenv("TG_GRAPH_NAME", "Transaction_Fraud")
    TG_SECRET: str = os.getenv("TG_SECRET", "")

    # Thresholds
    HIGH_RISK_THRESHOLD: float = 0.85
    LOW_RISK_THRESHOLD: float = 0.35

    # Directory Paths
    DATA_DIR: Path = BASE_DIR / "data"
    OUTPUT_DIR: Path = BASE_DIR / "outputs"
    BENCHMARK_DIR: Path = DATA_DIR / "benchmark"
    BENCHMARK_OUTPUT_DIR: Path = OUTPUT_DIR / "benchmark_results"
    SAR_OUTPUT_DIR: Path = OUTPUT_DIR / "sars"

config = Config()