import streamlit as st
import pandas as pd
import re
import json
from pathlib import Path
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="📚 Literature Review Parser",
    layout="wide"
)

st.title("📚 ChatGPT Literature Review Parser")

# =========================================================
# PATHS
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

JSON_PATH = DATA_DIR / "parsed_literature.json"

# =========================================================
# INPUT
# =========================================================
raw_text = st.text_area(
    "Paste literature review text below:",
    height=450
)

# =========================================================
# PARSING FUNCTIONS
# =========================================================
def extract_sections(text: str) -> dict:
    sections = {}
    current = None
    buffer = []

    for line in text.splitlines():
        header = re.match(r"^##\s+(.*)", line)
        if header:
            if current:
                sections[current] = "\n".join(buffer).strip()
            current = header.group(1).strip()
            buffer = []
        else:
            buffer.append(line)

    if current:
        sections[current] = "\n".join(buffer).strip()

    return sections


def extract_inline_citations(text: str) -> list:
    pattern = re.compile(
        r"\(([^,]+?),\s*(\d{4}),\s*\[?(https?://[^\]\)]+)\]?\)"
    )
    return [
        {
            "authors": a.strip(),
            "year": y,
            "url": u.strip()
        }
        for a, y, u in pattern.findall(text)
    ]


def extract_annotated_bibliography(text: str) -> list:
    pattern = re.compile(
        r"\*\*(.*?)\s*\((\d{4})\)\*\*\s+—\s+(.*?)\n\[(https?://.*?)\]",
        re.DOTALL
    )
    return [
        {
            "authors": a.strip(),
            "year": y,
            "description": d.strip(),
            "url": u.strip()
        }
        for a, y, d, u in pattern.findall(text)
    ]


def load_existing_json(path: Path) -> list:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with open(path, "r") as f:
        return json.load(f)


def save_json(path: Path, data: list):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# =========================================================
# PARSE BUTTON
# =========================================================
if st.button("🔍 Parse & Save") and raw_text.strip():

    # ---------- Parse ----------
    sections = extract_sections(raw_text)

    citations = []
    for title, content in sections.items():
        for c in extract_inline_citations(content):
            c["section"] = title
            citations.append(c)

    bibliography = extract_annotated_bibliography(raw_text)

    # ---------- Build JSON Record ----------
    record = {
        "batch_id": f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "created_at": datetime.utcnow().isoformat(),
        "source": "manual_paste",
        "sections": [
            {"section_title": k, "section_text": v}
            for k, v in sections.items()
        ],
        "citations": citations,
        "bibliography": bibliography
    }

    # ---------- Persist ----------
    all_batches = load_existing_json(JSON_PATH)
    all_batches.append(record)
    save_json(JSON_PATH, all_batches)

    # ---------- UI Feedback ----------
    st.success("✅ Parsing complete & JSON saved")

    # ---------- Display ----------
    st.subheader("📘 Parsed Sections")
    st.dataframe(pd.DataFrame(record["sections"]), use_container_width=True)

    st.subheader("🔗 Inline Citations")
    st.dataframe(pd.DataFrame(citations), use_container_width=True)

    st.subheader("📚 Annotated Bibliography")
    st.dataframe(pd.DataFrame(bibliography), use_container_width=True)

# =========================================================
# LOAD EXISTING DATA
# =========================================================
st.divider()
st.subheader("📂 Existing Parsed Batches")

existing = load_existing_json(JSON_PATH)

if not existing:
    st.info("No saved batches yet.")
else:
    st.json(existing)


# import streamlit as st
# import pandas as pd
# import re
# from pathlib import Path

# # =========================================================
# # CONFIG
# # =========================================================
# st.set_page_config(page_title="📚 Literature Review Parser", layout="wide")

# BASE_DIR = Path(__file__).resolve().parent
# CSV_PATH = BASE_DIR / "parsed_literature.csv"

# st.title("📚 Literature Review Section & Citation Parser")

# # =========================================================
# # INPUT
# # =========================================================
# raw_text = st.text_area(
#     "Paste literature review text below:",
#     height=400
# )

# # =========================================================
# # UTILITIES
# # =========================================================
# def safe_read_csv(path: Path) -> pd.DataFrame:
#     """Safely read CSV or return empty DataFrame."""
#     if not path.exists() or path.stat().st_size == 0:
#         return pd.DataFrame()
#     try:
#         return pd.read_csv(path)
#     except Exception:
#         return pd.DataFrame()

# def extract_sections(text: str):
#     """
#     Extract sections using markdown headers.
#     """
#     sections = {}
#     current_title = None
#     buffer = []

#     for line in text.splitlines():
#         header_match = re.match(r"^##\s+(.*)", line)
#         if header_match:
#             if current_title:
#                 sections[current_title] = "\n".join(buffer).strip()
#             current_title = header_match.group(1).strip()
#             buffer = []
#         else:
#             buffer.append(line)

#     if current_title:
#         sections[current_title] = "\n".join(buffer).strip()

#     return sections

# def extract_inline_citations(text: str):
#     """
#     Extract (Author et al., YEAR, URL)
#     """
#     pattern = re.compile(
#         r"\(([^,]+?),\s*(\d{4}),\s*\[?(https?://[^\]\)]+)\]?\)"
#     )
#     matches = pattern.findall(text)

#     records = []
#     for authors, year, url in matches:
#         records.append({
#             "authors": authors.strip(),
#             "year": year,
#             "url": url.strip()
#         })
#     return records

# def extract_annotated_bibliography(text: str):
#     """
#     Extract annotated bibliography entries.
#     """
#     entries = []
#     pattern = re.compile(
#         r"\*\*(.*?)\s*\((\d{4})\)\*\*\s+—\s+(.*?)\n\[(https?://.*?)\]",
#         re.DOTALL
#     )

#     for match in pattern.findall(text):
#         entries.append({
#             "authors": match[0].strip(),
#             "year": match[1],
#             "description": match[2].strip(),
#             "url": match[3].strip()
#         })

#     return entries

# # =========================================================
# # PARSE BUTTON
# # =========================================================
# if st.button("🔍 Parse Literature Review") and raw_text.strip():

#     # -------- Sections --------
#     sections = extract_sections(raw_text)
#     section_rows = [
#         {"section_title": k, "section_text": v}
#         for k, v in sections.items()
#     ]
#     df_sections = pd.DataFrame(section_rows)

#     # -------- Citations --------
#     citation_rows = []
#     for section, content in sections.items():
#         for c in extract_inline_citations(content):
#             c["section"] = section
#             citation_rows.append(c)

#     df_citations = pd.DataFrame(citation_rows)

#     # -------- Annotated Bibliography --------
#     df_biblio = pd.DataFrame(
#         extract_annotated_bibliography(raw_text)
#     )

#     # -------- Save --------
#     with pd.ExcelWriter(CSV_PATH.with_suffix(".xlsx")) as writer:
#         df_sections.to_excel(writer, sheet_name="sections", index=False)
#         df_citations.to_excel(writer, sheet_name="citations", index=False)
#         df_biblio.to_excel(writer, sheet_name="bibliography", index=False)

#     st.success("✅ Parsing complete & saved")

#     # -------- Display --------
#     st.subheader("📘 Parsed Sections")
#     st.dataframe(df_sections, use_container_width=True)

#     st.subheader("🔗 Inline Citations")
#     st.dataframe(df_citations, use_container_width=True)

#     st.subheader("📚 Annotated Bibliography")
#     st.dataframe(df_biblio, use_container_width=True)

# # =========================================================
# # LOAD PREVIOUS RESULTS SAFELY
# # =========================================================
# st.divider()
# st.subheader("📂 Previously Saved Data")

# df_existing = safe_read_csv(CSV_PATH)

# if df_existing.empty:
#     st.info("No existing CSV data found.")
# else:
#     st.dataframe(df_existing)


# import streamlit as st
# import pandas as pd
# from pathlib import Path
# from datetime import datetime
# import json
# import re

# # =========================================================
# # PAGE CONFIG
# # =========================================================
# st.set_page_config(page_title="📘 ESG Literature Review Parser", layout="wide")
# st.title("📘 ESG Literature Review – Batch Parser")
# st.caption("Batch-aware parsing, storage, and retrieval")

# # =========================================================
# # STORAGE
# # =========================================================
# BASE_DIR = Path.cwd()
# DATA_DIR = BASE_DIR / "data"
# DATA_DIR.mkdir(exist_ok=True)

# CSV_PATH = DATA_DIR / "literature_batches.csv"
# JSON_PATH = DATA_DIR / "literature_batches.json"

# # =========================================================
# # HELPERS
# # =========================================================
# def next_batch_id(existing_ids):
#     if not existing_ids:
#         return "batch_001"
#     nums = [int(b.split("_")[1]) for b in existing_ids]
#     return f"batch_{max(nums)+1:03d}"

# def parse_sections(text: str):
#     sections = []
#     current_title = None
#     buffer = []

#     for line in text.splitlines():
#         line = line.rstrip()
#         if re.match(r"^##\\s+", line):
#             if current_title:
#                 sections.append({
#                     "section": current_title,
#                     "content": "\n".join(buffer).strip()
#                 })
#             current_title = line.replace("##", "").strip()
#             buffer = []
#         else:
#             if current_title:
#                 buffer.append(line)

#     if current_title:
#         sections.append({
#             "section": current_title,
#             "content": "\n".join(buffer).strip()
#         })

#     return sections

# # =========================================================
# # INPUT
# # =========================================================
# raw_text = st.text_area(
#     "📥 Paste literature review (Markdown with ## sections)",
#     height=350
# )

# # =========================================================
# # PARSE & STORE
# # =========================================================
# if st.button("🔍 Parse & Store as New Batch"):
#     if not raw_text.strip():
#         st.warning("Please paste text first.")
#     else:
#         sections = parse_sections(raw_text)

#         # Load existing JSON
#         if JSON_PATH.exists():
#             with open(JSON_PATH, "r") as f:
#                 store = json.load(f)
#         else:
#             store = []

#         existing_ids = [b["batch_id"] for b in store]
#         batch_id = next_batch_id(existing_ids)

#         timestamp = datetime.utcnow().isoformat()

#         batch_obj = {
#             "batch_id": batch_id,
#             "created_at": timestamp,
#             "source": "manual_paste",
#             "sections": sections
#         }

#         store.append(batch_obj)

#         # Save JSON (authoritative)
#         with open(JSON_PATH, "w") as f:
#             json.dump(store, f, indent=2)

#         # Save CSV (flat)
#         rows = []
#         for s in sections:
#             rows.append({
#                 "batch_id": batch_id,
#                 "section": s["section"],
#                 "content": s["content"],
#                 "created_at": timestamp
#             })

#         df_new = pd.DataFrame(rows)

#         if CSV_PATH.exists():
#             df_old = pd.read_csv(CSV_PATH)
#             df_new = pd.concat([df_old, df_new], ignore_index=True)

#         df_new.to_csv(CSV_PATH, index=False)

#         st.success(f"Stored {len(sections)} sections as {batch_id}")

# # =========================================================
# # BROWSE
# # =========================================================
# st.divider()
# st.subheader("📂 Stored Batches")

# if CSV_PATH.exists():
#     df = pd.read_csv(CSV_PATH)

#     batch_filter = st.multiselect(
#         "Filter by batch",
#         sorted(df["batch_id"].unique())
#     )

#     if batch_filter:
#         df = df[df["batch_id"].isin(batch_filter)]

#     st.dataframe(df, use_container_width=True)

#     st.download_button(
#         "⬇️ Download CSV",
#         df.to_csv(index=False),
#         "literature_batches.csv",
#         "text/csv"
#     )
# else:
#     st.info("No batches stored yet.")


# import streamlit as st
# import pandas as pd
# from pathlib import Path
# from datetime import datetime
# import json

# # =========================================================
# # PAGE CONFIG
# # =========================================================
# st.set_page_config(page_title="📘 ESG Literature Review Parser", layout="wide")
# st.title("📘 Constraint-Aware ESG Literature Review")
# st.caption("Parse, browse, and persist structured literature review content")

# # =========================================================
# # STORAGE PATHS
# # =========================================================
# BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path.cwd()
# DATA_DIR = BASE_DIR / "data"
# DATA_DIR.mkdir(exist_ok=True)

# CSV_PATH = DATA_DIR / "literature_review_sections.csv"
# JSON_PATH = DATA_DIR / "literature_review_sections.json"

# # =========================================================
# # RAW INPUT (MANUAL PASTE OR LOAD)
# # =========================================================
# with st.expander("📥 Input Literature Review Text", expanded=True):
#     raw_text = st.text_area(
#         "Paste the full literature review text here",
#         height=400,
#         placeholder="Paste the ESG literature review markdown or text here"
#     )

# # =========================================================
# # SECTION PARSER
# # =========================================================
# def parse_sections(text: str):
#     sections = []
#     current_title = None
#     current_content = []

#     for line in text.splitlines():
#         line = line.strip()
#         if line.startswith("## "):
#             if current_title:
#                 sections.append({
#                     "section": current_title,
#                     "content": "\n".join(current_content).strip()
#                 })
#             current_title = line.replace("## ", "").strip()
#             current_content = []
#         else:
#             if current_title:
#                 current_content.append(line)

#     if current_title:
#         sections.append({
#             "section": current_title,
#             "content": "\n".join(current_content).strip()
#         })

#     return sections

# # =========================================================
# # PARSE ACTION
# # =========================================================
# if st.button("🔍 Parse Sections"):
#     if not raw_text.strip():
#         st.warning("Please paste literature review text first.")
#     else:
#         parsed = parse_sections(raw_text)
#         df = pd.DataFrame(parsed)
#         df["parsed_at"] = datetime.utcnow().isoformat()

#         # Persist CSV
#         if CSV_PATH.exists():
#             old = pd.read_csv(CSV_PATH)
#             df = pd.concat([old, df], ignore_index=True)
#         df.to_csv(CSV_PATH, index=False)

#         # Persist JSON
#         if JSON_PATH.exists():
#             with open(JSON_PATH, "r") as f:
#                 old_json = json.load(f)
#         else:
#             old_json = []

#         old_json.extend(parsed)
#         with open(JSON_PATH, "w") as f:
#             json.dump(old_json, f, indent=2)

#         st.success(f"Parsed and stored {len(parsed)} sections")

# # =========================================================
# # BROWSE STORED RESULTS
# # =========================================================
# st.divider()
# st.subheader("📂 Stored Literature Review Sections")

# if CSV_PATH.exists():
#     df_store = pd.read_csv(CSV_PATH)

#     section_filter = st.multiselect(
#         "Filter by section",
#         options=sorted(df_store["section"].unique())
#     )

#     if section_filter:
#         df_store = df_store[df_store["section"].isin(section_filter)]

#     st.dataframe(df_store, use_container_width=True)

#     st.download_button(
#         "⬇️ Download CSV",
#         data=df_store.to_csv(index=False),
#         file_name="literature_review_sections.csv",
#         mime="text/csv"
#     )
# else:
#     st.info("No stored results yet. Parse text above to begin.")

# # =========================================================
# # FUTURE EXTENSIONS
# # =========================================================
# with st.expander("🧠 Future Extensions"):
#     st.markdown("""
#     - ESG claim sentence extraction
#     - XBRL tag alignment (taxonomy-level constraints)
#     - Similarity search across sections
#     - Optional LLM-based summarization / verification
#     - Export to vector DB or audit pipeline
#     """)