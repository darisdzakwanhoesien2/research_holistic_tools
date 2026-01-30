import streamlit as st
import pandas as pd
import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# =====================================================
# INIT
# =====================================================
load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
BASELINE_DIR = DATA_DIR / "outputs/baseline"
ENRICHED_DIR = DATA_DIR / "outputs/enriched"

BASELINE_DIR.mkdir(parents=True, exist_ok=True)
ENRICHED_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="📚 Abstract Intelligence Lab", layout="wide")
st.title("📚 Abstract Intelligence Lab")

# =====================================================
# LLM UTILITIES (OPTIONAL)
# =====================================================
def get_llm_endpoint(provider):
    if provider == "openrouter":
        return {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "headers": {
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            }
        }

    env = os.getenv("LLM_ENV", "local").upper()
    base_url = os.getenv(f"LMSTUDIO_{env}_URL")

    return {
        "url": f"{base_url}/chat/completions",
        "headers": {"Content-Type": "application/json"}
    }

def call_llm(prompt, provider, model):
    cfg = get_llm_endpoint(provider)
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    r = requests.post(cfg["url"], headers=cfg["headers"], json=payload, timeout=90)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# =====================================================
# STEP 1 — LOAD CSV
# =====================================================
st.header("① Load Literature CSV")

uploaded = st.file_uploader(
    "Upload CSV (Litmaps / Scopus format)",
    type=["csv"]
)

df_raw = None

if uploaded:
    df_raw = pd.read_csv(uploaded)
    df_raw = df_raw.dropna(subset=["Abstract"])
    st.success(f"Loaded {len(df_raw)} papers")
    st.dataframe(df_raw.head())

# =====================================================
# STEP 2 — SAVE BASELINE + SIMILARITY (NO LLM)
# =====================================================
if df_raw is not None and st.button("💾 Save Baseline + Similarity"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ---- Save baseline CSV
    base_csv = BASELINE_DIR / f"literature_raw_{timestamp}.csv"
    df_raw.to_csv(base_csv, index=False)

    # ---- Similarity
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(df_raw["Abstract"])
    sim = cosine_similarity(X)

    sim_df = pd.DataFrame(sim)
    sim_csv = BASELINE_DIR / f"similarity_{timestamp}.csv"
    sim_df.to_csv(sim_csv, index=False)

    st.success("Baseline and similarity saved")

    st.download_button("⬇️ Download Baseline CSV", df_raw.to_csv(index=False), base_csv.name)
    st.download_button("⬇️ Download Similarity CSV", sim_df.to_csv(index=False), sim_csv.name)

# =====================================================
# STEP 3 — OPTIONAL LLM ENRICHMENT
# =====================================================
st.header("② Optional LLM Enrichment")

enable_llm = st.checkbox("Enable LLM enrichment")

if enable_llm and df_raw is not None:
    provider = st.selectbox("LLM Provider", ["lmstudio", "openrouter"])

    # ---- Model selection
    with open(DATA_DIR / "models.json") as f:
        models_cfg = json.load(f)

    models = models_cfg[provider]["allowed_models"]
    model_map = {m["label"]: m["id"] for m in models}

    model_label = st.selectbox("Model", list(model_map.keys()))
    model_id = model_map[model_label]

    # ---- Paper selection
    df_raw["paper_label"] = (
        df_raw["Title"].fillna("Untitled") +
        " (" + df_raw["Year"].astype(str) + ")"
    )

    selected = st.multiselect(
        "Select papers to enrich",
        df_raw["paper_label"].tolist()
    )

    if selected and st.button("🚀 Run LLM"):
        df_enriched = df_raw.copy()

        with st.spinner("Running LLM on selected papers..."):
            for idx, row in df_enriched.iterrows():
                if row["paper_label"] not in selected:
                    continue

                prompt = f"""
Extract structured research metadata.
Return VALID JSON ONLY.

Fields:
- task
- domain
- method
- contribution
- limitation
- keywords (list)

Abstract:
{row['Abstract']}
"""
                try:
                    result = call_llm(prompt, provider, model_id)
                    meta = json.loads(result)
                except Exception:
                    meta = {}

                for k, v in meta.items():
                    df_enriched.at[idx, k] = v

        # ---- Save enriched CSV
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        enriched_path = ENRICHED_DIR / f"enriched_{provider}_{ts}.csv"
        df_enriched.drop(columns=["paper_label"]).to_csv(enriched_path, index=False)

        st.success("Enriched results saved")
        st.download_button(
            "⬇️ Download Enriched CSV",
            df_enriched.to_csv(index=False),
            enriched_path.name
        )

        st.dataframe(df_enriched)

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("Baseline-first • LLM-optional • Publication-safe")
