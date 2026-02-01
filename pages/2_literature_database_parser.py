import streamlit as st
import pandas as pd
import json
from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="📂 Literature Review Database Browser",
    layout="wide"
)

st.title("📂 Literature Review Database Browser")
st.caption("Read-only retrieval & visualization from parsed_literature.json")

# =========================================================
# PATHS
# =========================================================
BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / "data"
JSON_PATH = DATA_DIR / "parsed_literature.json"

# =========================================================
# LOAD DATABASE
# =========================================================
def load_database(path: Path):
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)

database = load_database(JSON_PATH)

if not database:
    st.warning("No data found in parsed_literature.json")
    st.stop()

# =========================================================
# HELPERS
# =========================================================
def flatten_batches(batches):
    sections, citations, bibliography = [], [], []

    for b in batches:
        bid = b.get("batch_id", "unknown")

        for s in b.get("sections", []):
            sections.append({
                "batch_id": bid,
                "section_title": s.get("section_title"),
                "section_text": s.get("section_text")
            })

        for c in b.get("citations", []):
            citations.append({
                "batch_id": bid,
                "section": c.get("section"),
                "authors": c.get("authors"),
                "year": c.get("year"),
                "url": c.get("url")
            })

        for r in b.get("bibliography", []):
            bibliography.append({
                "batch_id": bid,
                "authors": r.get("authors"),
                "year": r.get("year"),
                "description": r.get("description"),
                "url": r.get("url")
            })

    return sections, citations, bibliography

# =========================================================
# BATCH SELECTOR
# =========================================================
st.subheader("🔽 Select Batch")

batch_ids = ["ALL (combined)"] + [b["batch_id"] for b in database]

selected_batch = st.selectbox(
    "Choose batch to retrieve:",
    batch_ids
)

if selected_batch == "ALL (combined)":
    selected_batches = database
else:
    selected_batches = [
        b for b in database if b["batch_id"] == selected_batch
    ]

# =========================================================
# RETRIEVE DATA
# =========================================================
sections, citations, bibliography = flatten_batches(selected_batches)

# =========================================================
# DISPLAY: SECTIONS
# =========================================================
st.divider()
st.subheader("📘 Sections")

if sections:
    df_sections = pd.DataFrame(sections)
    st.dataframe(df_sections, use_container_width=True)
else:
    st.info("No sections found.")

# =========================================================
# DISPLAY: INLINE CITATIONS
# =========================================================
st.subheader("🔗 Inline Citations")

if citations:
    df_citations = pd.DataFrame(citations)
    st.dataframe(df_citations, use_container_width=True)
else:
    st.info("No inline citations found.")

# =========================================================
# DISPLAY: ANNOTATED BIBLIOGRAPHY
# =========================================================
st.subheader("📚 Annotated Bibliography")

if bibliography:
    df_bib = pd.DataFrame(bibliography)
    st.dataframe(df_bib, use_container_width=True)
else:
    st.info("No bibliography entries found.")

# =========================================================
# RAW JSON (AUDIT / DEBUG)
# =========================================================
st.divider()
st.subheader("🧾 Raw JSON View (Audit Mode)")
st.json(selected_batches)


# import streamlit as st
# import pandas as pd
# import re
# import json
# from pathlib import Path
# from datetime import datetime

# # =========================================================
# # PAGE CONFIG
# # =========================================================
# st.set_page_config(
#     page_title="📚 Literature Review Parser",
#     layout="wide"
# )

# st.title("📚 ChatGPT Literature Review Parser")
# st.caption("Batch-aware parsing, storage, and visualization")

# # =========================================================
# # PATHS
# # =========================================================
# BASE_DIR = Path.cwd()
# DATA_DIR = BASE_DIR / "data"
# DATA_DIR.mkdir(exist_ok=True)

# JSON_PATH = DATA_DIR / "parsed_literature.json"

# # =========================================================
# # UTILITIES
# # =========================================================
# def load_existing_json(path: Path) -> list:
#     if not path.exists() or path.stat().st_size == 0:
#         return []
#     with open(path, "r") as f:
#         return json.load(f)


# def save_json(path: Path, data: list):
#     with open(path, "w") as f:
#         json.dump(data, f, indent=2)


# # =========================================================
# # PARSING FUNCTIONS
# # =========================================================
# def extract_sections(text: str) -> dict:
#     sections = {}
#     current = None
#     buffer = []

#     for line in text.splitlines():
#         header = re.match(r"^##\s+(.*)", line)
#         if header:
#             if current:
#                 sections[current] = "\n".join(buffer).strip()
#             current = header.group(1).strip()
#             buffer = []
#         else:
#             if current:
#                 buffer.append(line)

#     if current:
#         sections[current] = "\n".join(buffer).strip()

#     return sections


# def extract_inline_citations(text: str) -> list:
#     pattern = re.compile(
#         r"\(([^,]+?),\s*(\d{4}),\s*\[?(https?://[^\]\)]+)\]?\)"
#     )
#     return [
#         {
#             "authors": a.strip(),
#             "year": y,
#             "url": u.strip()
#         }
#         for a, y, u in pattern.findall(text)
#     ]


# def extract_annotated_bibliography(text: str) -> list:
#     pattern = re.compile(
#         r"\*\*(.*?)\s*\((\d{4})\)\*\*\s+—\s+(.*?)\n\[(https?://.*?)\]",
#         re.DOTALL
#     )
#     return [
#         {
#             "authors": a.strip(),
#             "year": y,
#             "description": d.strip(),
#             "url": u.strip()
#         }
#         for a, y, d, u in pattern.findall(text)
#     ]


# def flatten_batches(batches):
#     sections, citations, bibliography = [], [], []

#     for b in batches:
#         bid = b["batch_id"]

#         for s in b.get("sections", []):
#             sections.append({
#                 "batch_id": bid,
#                 "section_title": s["section_title"],
#                 "section_text": s["section_text"]
#             })

#         for c in b.get("citations", []):
#             c_copy = c.copy()
#             c_copy["batch_id"] = bid
#             citations.append(c_copy)

#         for r in b.get("bibliography", []):
#             r_copy = r.copy()
#             r_copy["batch_id"] = bid
#             bibliography.append(r_copy)

#     return sections, citations, bibliography


# # =========================================================
# # INPUT
# # =========================================================
# st.subheader("📥 Paste Literature Review Text")

# raw_text = st.text_area(
#     "Use Markdown with ## section headings",
#     height=420
# )

# # =========================================================
# # PARSE & SAVE
# # =========================================================
# if st.button("🔍 Parse & Save as New Batch") and raw_text.strip():

#     sections = extract_sections(raw_text)

#     citations = []
#     for title, content in sections.items():
#         for c in extract_inline_citations(content):
#             c["section"] = title
#             citations.append(c)

#     bibliography = extract_annotated_bibliography(raw_text)

#     batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

#     record = {
#         "batch_id": batch_id,
#         "created_at": datetime.utcnow().isoformat(),
#         "source": "manual_paste",
#         "sections": [
#             {"section_title": k, "section_text": v}
#             for k, v in sections.items()
#         ],
#         "citations": citations,
#         "bibliography": bibliography
#     }

#     all_batches = load_existing_json(JSON_PATH)
#     all_batches.append(record)
#     save_json(JSON_PATH, all_batches)

#     st.success(f"✅ Saved {len(sections)} sections as {batch_id}")

# # =========================================================
# # BATCH VIEWER
# # =========================================================
# st.divider()
# st.subheader("📊 Batch Viewer")

# existing = load_existing_json(JSON_PATH)

# if not existing:
#     st.info("No saved batches yet.")
# else:
#     batch_ids = ["ALL (combined)"] + [b["batch_id"] for b in existing]

#     selected_batch = st.selectbox(
#         "Select batch to visualize",
#         batch_ids
#     )

#     if selected_batch == "ALL (combined)":
#         view_batches = existing
#     else:
#         view_batches = [b for b in existing if b["batch_id"] == selected_batch]

#     sections, citations, bibliography = flatten_batches(view_batches)

#     # =====================================================
#     # DISPLAY
#     # =====================================================
#     st.subheader("📘 Sections")
#     if sections:
#         st.dataframe(pd.DataFrame(sections), use_container_width=True)
#     else:
#         st.info("No sections available.")

#     st.subheader("🔗 Inline Citations")
#     if citations:
#         st.dataframe(pd.DataFrame(citations), use_container_width=True)
#     else:
#         st.info("No citations available.")

#     st.subheader("📚 Annotated Bibliography")
#     if bibliography:
#         st.dataframe(pd.DataFrame(bibliography), use_container_width=True)
#     else:
#         st.info("No bibliography entries available.")

#     st.subheader("🧾 Raw JSON (Debug / Audit)")
#     st.json(view_batches)
