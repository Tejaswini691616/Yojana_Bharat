# PATH: GovScheme/config.py
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-only-change-me")
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"

    DATABASE_PATH = os.path.join(BASE_DIR, os.getenv("DATABASE_PATH", "database/SmartGov_AI.db"))
    EXCEL_SOURCE_PATH = os.path.join(BASE_DIR, "data", "Government_Scheme_Eligibility_Upgraded.xlsx")

    ML_MODEL_PATH = os.path.join(BASE_DIR, os.getenv("ML_MODEL_PATH", "ml_models/trained_model.joblib"))
    ML_METRICS_PATH = os.path.join(BASE_DIR, "ml_models", "metrics.json")

    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "")

    STT_PROVIDER = os.getenv("STT_PROVIDER", "")
    STT_API_KEY = os.getenv("STT_API_KEY", "")

    TTS_PROVIDER = os.getenv("TTS_PROVIDER", "")
    TTS_API_KEY = os.getenv("TTS_API_KEY", "")

    SCHEME_UPDATE_INTERVAL_HOURS = int(os.getenv("SCHEME_UPDATE_INTERVAL_HOURS", "24"))

    RPA_MODE = os.getenv("RPA_MODE", "DEMO")
    UIPATH_ORCHESTRATOR_URL = os.getenv("UIPATH_ORCHESTRATOR_URL", "")
    UIPATH_ORCHESTRATOR_TENANT = os.getenv("UIPATH_ORCHESTRATOR_TENANT", "")
    UIPATH_ORCHESTRATOR_CLIENT_ID = os.getenv("UIPATH_ORCHESTRATOR_CLIENT_ID", "")
    UIPATH_ORCHESTRATOR_CLIENT_SECRET = os.getenv("UIPATH_ORCHESTRATOR_CLIENT_SECRET", "")

    DISCLAIMER = (
        "SmartGov AI provides prototype eligibility and recommendation assistance based on "
        "available scheme data and configured criteria. Final eligibility, benefits, documents "
        "and application requirements must be verified using the official government source "
        "before applying."
    )
