import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="📘 ESG Literature Review Parser", layout="wide")
st.title("📘 Constraint-Aware ESG Literature Review")
st.caption("Parse, browse, and persist structured literature review content")

# =========================================================
# STORAGE PATHS
# =========================================================
BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path.cwd()
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

CSV_PATH = DATA_DIR / "literature_review_sections.csv"
JSON_PATH = DATA_DIR / "literature_review_sections.json"

# =========================================================
# RAW INPUT (MANUAL PASTE OR LOAD)
# =========================================================
with st.expander("📥 Input Literature Review Text", expanded=True):
    raw_text = st.text_area(
        "Paste the full literature review text here",
        height=400,
        placeholder="Paste the ESG literature review markdown or text here"
    )

# =========================================================
# SECTION PARSER
# =========================================================
def parse_sections(text: str):
    sections = []
    current_title = None
    current_content = []

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("## "):
            if current_title:
                sections.append({
                    "section": current_title,
                    "content": "\n".join(current_content).strip()
                })
            current_title = line.replace("## ", "").strip()
            current_content = []
        else:
            if current_title:
                current_content.append(line)

    if current_title:
        sections.append({
            "section": current_title,
            "content": "\n".join(current_content).strip()
        })

    return sections

# =========================================================
# PARSE ACTION
# =========================================================
if st.button("🔍 Parse Sections"):
    if not raw_text.strip():
        st.warning("Please paste literature review text first.")
    else:
        parsed = parse_sections(raw_text)
        df = pd.DataFrame(parsed)
        df["parsed_at"] = datetime.utcnow().isoformat()

        # Persist CSV
        if CSV_PATH.exists():
            old = pd.read_csv(CSV_PATH)
            df = pd.concat([old, df], ignore_index=True)
        df.to_csv(CSV_PATH, index=False)

        # Persist JSON
        if JSON_PATH.exists():
            with open(JSON_PATH, "r") as f:
                old_json = json.load(f)
        else:
            old_json = []

        old_json.extend(parsed)
        with open(JSON_PATH, "w") as f:
            json.dump(old_json, f, indent=2)

        st.success(f"Parsed and stored {len(parsed)} sections")

# =========================================================
# BROWSE STORED RESULTS
# =========================================================
st.divider()
st.subheader("📂 Stored Literature Review Sections")

if CSV_PATH.exists():
    df_store = pd.read_csv(CSV_PATH)

    section_filter = st.multiselect(
        "Filter by section",
        options=sorted(df_store["section"].unique())
    )

    if section_filter:
        df_store = df_store[df_store["section"].isin(section_filter)]

    st.dataframe(df_store, use_container_width=True)

    st.download_button(
        "⬇️ Download CSV",
        data=df_store.to_csv(index=False),
        file_name="literature_review_sections.csv",
        mime="text/csv"
    )
else:
    st.info("No stored results yet. Parse text above to begin.")

# =========================================================
# FUTURE EXTENSIONS
# =========================================================
with st.expander("🧠 Future Extensions"):
    st.markdown("""
    - ESG claim sentence extraction
    - XBRL tag alignment (taxonomy-level constraints)
    - Similarity search across sections
    - Optional LLM-based summarization / verification
    - Export to vector DB or audit pipeline
    """)