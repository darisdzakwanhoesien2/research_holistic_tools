import streamlit as st
import os
import glob
import json
import re
import pandas as pd

DATA_DIR = "data/ocr_pdf"
OUTPUT_FILE = "data/cluster_journal_label.json"

st.title("📑 Robust Journal Section Extractor (With Others + Coverage)")

# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def read_all_pages(pdf_folder):
    pages_path = os.path.join(pdf_folder, "pages")
    page_files = sorted(glob.glob(os.path.join(pages_path, "*.md")))

    full_text = ""
    for file in page_files:
        with open(file, "r", encoding="utf-8") as f:
            full_text += f.read() + "\n"

    return full_text


def split_sections_with_others(text):
    """
    Detect structured sections and compute leftover text using index boundaries.
    """

    pattern = r"""
    (
        ^\s*#+\s+.*$           |   # Markdown headers
        ^\s*\d+\.\s+.*$        |   # 1. Introduction
        ^\s*Abstract\s*$       |   # Abstract
        ^\s*Literature review.*$
    )
    """

    matches = list(
        re.finditer(
            pattern,
            text,
            re.MULTILINE | re.IGNORECASE | re.VERBOSE
        )
    )

    sections = {}
    covered_ranges = []

    for i, match in enumerate(matches):
        header = match.group().strip().lower()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        content = text[start:end].strip()
        covered_ranges.append((start, end))

        if "abstract" in header:
            sections["abstract"] = content
        elif "introduction" in header:
            sections["introduction"] = content
        elif "literature" in header:
            sections["literature_review"] = content

    # ----------------------------------------------
    # Compute leftover text using gaps
    # ----------------------------------------------

    remaining_chunks = []
    last_end = 0

    for start, end in sorted(covered_ranges):
        if start > last_end:
            remaining_chunks.append(text[last_end:start])
        last_end = end

    if last_end < len(text):
        remaining_chunks.append(text[last_end:])

    remaining_text = "\n".join(remaining_chunks).strip()

    return sections, remaining_text


def compute_metadata(text):
    words = re.findall(r"\b\w+\b", text)
    sentences = re.split(r"[.!?]+", text)

    return {
        "word_count": len(words),
        "sentence_count": len([s for s in sentences if s.strip()]),
        "char_count": len(text)
    }


def parse_all_pdfs():
    cluster_data = []
    coverage_stats = []

    pdf_folders = [
        os.path.join(DATA_DIR, d)
        for d in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, d))
    ]

    for pdf_folder in pdf_folders:

        journal_name = os.path.basename(pdf_folder)
        full_text = read_all_pages(pdf_folder)

        extracted_sections, remaining_text = split_sections_with_others(full_text)

        total_chars = len(full_text)
        structured_chars = 0

        # ------------------------------
        # Store structured sections
        # ------------------------------

        for label, text in extracted_sections.items():
            metadata = compute_metadata(text)
            structured_chars += metadata["char_count"]

            cluster_data.append({
                "journal_name": journal_name,
                "section_label": label,
                "word_count": metadata["word_count"],
                "sentence_count": metadata["sentence_count"],
                "char_count": metadata["char_count"],
                "text": text
            })

        # ------------------------------
        # Store others
        # ------------------------------

        if len(remaining_text) > 100:

            metadata = compute_metadata(remaining_text)

            cluster_data.append({
                "journal_name": journal_name,
                "section_label": "others",
                "word_count": metadata["word_count"],
                "sentence_count": metadata["sentence_count"],
                "char_count": metadata["char_count"],
                "text": remaining_text
            })

        # ------------------------------
        # Coverage Diagnostics
        # ------------------------------

        coverage_ratio = structured_chars / total_chars if total_chars > 0 else 0

        coverage_stats.append({
            "journal_name": journal_name,
            "total_characters": total_chars,
            "structured_characters": structured_chars,
            "coverage_ratio": round(coverage_ratio, 3)
        })

    return cluster_data, coverage_stats


# --------------------------------------------------
# UI
# --------------------------------------------------

if st.button("🔄 Parse Journals (Robust Mode)"):

    data, coverage = parse_all_pdfs()

    os.makedirs("data", exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    st.success("✅ JSON Generated Successfully!")

# --------------------------------------------------
# Load and Display
# --------------------------------------------------

if os.path.exists(OUTPUT_FILE):

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        cluster_data = json.load(f)

    df = pd.DataFrame(cluster_data)

    st.subheader("📊 Extracted Sections")
    st.dataframe(df[["journal_name", "section_label", "word_count"]])

    st.subheader("📄 Preview Text")

    selected_row = st.selectbox("Select Row", df.index)
    st.text_area("Section Content", df.loc[selected_row, "text"], height=400)

else:
    st.info("Click 'Parse Journals (Robust Mode)' to generate dataset.")


# import streamlit as st
# import os
# import glob
# import json
# import re
# import pandas as pd

# DATA_DIR = "data/ocr_pdf"
# OUTPUT_FILE = "data/cluster_journal_label.json"

# st.title("📑 Robust Journal Section Extractor")

# # --------------------------------------------------
# # HELPER FUNCTIONS
# # --------------------------------------------------

# def read_all_pages(pdf_folder):
#     pages_path = os.path.join(pdf_folder, "pages")
#     page_files = sorted(glob.glob(os.path.join(pages_path, "*.md")))

#     full_text = ""
#     for file in page_files:
#         with open(file, "r", encoding="utf-8") as f:
#             full_text += f.read() + "\n"
#     return full_text


# def split_sections(text):
#     """
#     Detect both markdown headers and numbered headers.
#     """

#     pattern = r"""
#     (
#         ^\s*#+\s+.*$           |   # Markdown header
#         ^\s*\d+\.\s+.*$        |   # 1. Introduction
#         ^\s*Abstract\s*$       |   # Abstract
#         ^\s*Literature review.*$
#     )
#     """

#     matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE | re.VERBOSE))

#     sections = {}

#     for i, match in enumerate(matches):
#         header = match.group().strip().lower()
#         start = match.start()
#         end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
#         content = text[start:end].strip()

#         if "abstract" in header:
#             sections["abstract"] = content
#         elif "introduction" in header:
#             sections["introduction"] = content
#         elif "literature" in header:
#             sections["literature_review"] = content

#     return sections


# def compute_metadata(text):
#     words = re.findall(r"\b\w+\b", text)
#     sentences = re.split(r"[.!?]+", text)

#     return {
#         "word_count": len(words),
#         "sentence_count": len([s for s in sentences if s.strip()]),
#         "char_count": len(text)
#     }


# def parse_all_pdfs():
#     cluster_data = []

#     pdf_folders = [
#         os.path.join(DATA_DIR, d)
#         for d in os.listdir(DATA_DIR)
#         if os.path.isdir(os.path.join(DATA_DIR, d))
#     ]

#     for pdf_folder in pdf_folders:

#         journal_name = os.path.basename(pdf_folder)
#         full_text = read_all_pages(pdf_folder)

#         extracted_sections = split_sections(full_text)

#         captured_text = ""

#         for label, text in extracted_sections.items():

#             metadata = compute_metadata(text)

#             cluster_data.append({
#                 "journal_name": journal_name,
#                 "section_label": label,
#                 "word_count": metadata["word_count"],
#                 "sentence_count": metadata["sentence_count"],
#                 "char_count": metadata["char_count"],
#                 "text": text
#             })

#             captured_text += text

#         # --------------------------------------------------
#         # STORE REMAINING TEXT AS "others"
#         # --------------------------------------------------

#         remaining_text = full_text.replace(captured_text, "").strip()

#         if len(remaining_text) > 200:  # avoid tiny fragments

#             metadata = compute_metadata(remaining_text)

#             cluster_data.append({
#                 "journal_name": journal_name,
#                 "section_label": "others",
#                 "word_count": metadata["word_count"],
#                 "sentence_count": metadata["sentence_count"],
#                 "char_count": metadata["char_count"],
#                 "text": remaining_text
#             })

#     return cluster_data


# # --------------------------------------------------
# # UI
# # --------------------------------------------------

# if st.button("🔄 Parse with Robust Extraction"):

#     data = parse_all_pdfs()

#     os.makedirs("data", exist_ok=True)

#     with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=4)

#     st.success("Saved robust labeled JSON!")


# if os.path.exists(OUTPUT_FILE):

#     with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
#         cluster_data = json.load(f)

#     df = pd.DataFrame(cluster_data)

#     st.subheader("📊 Extracted Sections")
#     st.dataframe(df[["journal_name", "section_label", "word_count"]])

#     st.subheader("📄 Preview")
#     selected_row = st.selectbox("Select Row", df.index)
#     st.text_area("Text", df.loc[selected_row, "text"], height=400)


# import streamlit as st
# import os
# import glob
# import json
# import re
# import pandas as pd

# DATA_DIR = "data/ocr_pdf"
# OUTPUT_FILE = "data/cluster_journal_label.json"

# st.title("📑 Journal Section Label Extractor")

# # --------------------------------------------------
# # Helper Functions
# # --------------------------------------------------

# def read_all_pages(pdf_folder):
#     pages_path = os.path.join(pdf_folder, "pages")
#     page_files = sorted(glob.glob(os.path.join(pages_path, "*.md")))

#     full_text = ""
#     for file in page_files:
#         with open(file, "r", encoding="utf-8") as f:
#             full_text += f.read() + "\n"
#     return full_text


# def extract_section(text, section_keywords):
#     """
#     Extracts text between markdown headers.
#     """

#     pattern = r"(#+\s.*)"
#     headers = [(m.start(), m.group()) for m in re.finditer(pattern, text)]

#     for i, (pos, header) in enumerate(headers):
#         header_lower = header.lower()

#         if any(keyword in header_lower for keyword in section_keywords):

#             start = pos
#             end = headers[i + 1][0] if i + 1 < len(headers) else len(text)
#             return text[start:end].strip()

#     return ""


# def compute_metadata(text):
#     words = re.findall(r"\b\w+\b", text)
#     sentences = re.split(r"[.!?]+", text)

#     return {
#         "word_count": len(words),
#         "sentence_count": len([s for s in sentences if s.strip()]),
#         "char_count": len(text)
#     }


# def parse_all_pdfs():
#     cluster_data = []

#     pdf_folders = [
#         os.path.join(DATA_DIR, d)
#         for d in os.listdir(DATA_DIR)
#         if os.path.isdir(os.path.join(DATA_DIR, d))
#     ]

#     for pdf_folder in pdf_folders:

#         journal_name = os.path.basename(pdf_folder)
#         full_text = read_all_pages(pdf_folder)

#         sections = {
#             "abstract": extract_section(full_text, ["abstract"]),
#             "introduction": extract_section(full_text, ["introduction"]),
#             "literature_review": extract_section(full_text, ["literature review"])
#         }

#         for label, text in sections.items():
#             if text.strip():

#                 metadata = compute_metadata(text)

#                 cluster_data.append({
#                     "journal_name": journal_name,
#                     "section_label": label,
#                     "word_count": metadata["word_count"],
#                     "sentence_count": metadata["sentence_count"],
#                     "char_count": metadata["char_count"],
#                     "text": text
#                 })

#     return cluster_data


# # --------------------------------------------------
# # UI Controls
# # --------------------------------------------------

# if st.button("🔄 Parse & Generate Label JSON"):

#     data = parse_all_pdfs()

#     os.makedirs("data", exist_ok=True)

#     with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=4)

#     st.success(f"Saved to {OUTPUT_FILE}")

# # --------------------------------------------------
# # Load and Display Existing JSON
# # --------------------------------------------------

# if os.path.exists(OUTPUT_FILE):

#     with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
#         cluster_data = json.load(f)

#     df = pd.DataFrame(cluster_data)

#     st.subheader("📊 Extracted Section Dataset")

#     st.dataframe(df[[
#         "journal_name",
#         "section_label",
#         "word_count",
#         "sentence_count",
#         "char_count"
#     ]])

#     st.subheader("📄 Preview Section Text")

#     selected_row = st.selectbox(
#         "Select Row to View Text",
#         df.index
#     )

#     st.text_area(
#         "Section Content",
#         df.loc[selected_row, "text"],
#         height=300
#     )

# else:
#     st.info("No JSON found yet. Click 'Parse & Generate Label JSON'.")
