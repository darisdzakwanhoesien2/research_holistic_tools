import streamlit as st
import os
import glob
import json
import re
import pandas as pd

DATA_DIR = "data/ocr_pdf"
CONFIG_PATH = "data/label_code.json"
OUTPUT_FILE = "data/cluster_journal_label.json"

st.title("📑 Dynamic Journal Section Extractor")

# --------------------------------------------------
# Load Label Config
# --------------------------------------------------

if not os.path.exists(CONFIG_PATH):
    st.error("No label_code.json found. Create labels first.")
    st.stop()

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    label_config = json.load(f)

st.sidebar.subheader("📌 Active Labels")
st.sidebar.json(label_config)

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


def split_sections(text):

    pattern = r"""
    (
        ^\s*#+\s+.*$           |
        ^\s*\d+\.\s+.*$
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

        for label_key, variants in label_config.items():
            for variant in variants:
                if variant in header:
                    sections[label_key] = content
                    break

    # -----------------------------------------
    # Compute leftover text
    # -----------------------------------------

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

    pdf_folders = [
        os.path.join(DATA_DIR, d)
        for d in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, d))
    ]

    for pdf_folder in pdf_folders:

        journal_name = os.path.basename(pdf_folder)
        full_text = read_all_pages(pdf_folder)

        extracted_sections, remaining_text = split_sections(full_text)

        # Store structured sections
        for label, text in extracted_sections.items():
            metadata = compute_metadata(text)

            cluster_data.append({
                "journal_name": journal_name,
                "section_label": label,
                "word_count": metadata["word_count"],
                "sentence_count": metadata["sentence_count"],
                "char_count": metadata["char_count"],
                "text": text
            })

        # Store others
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

    return cluster_data


# --------------------------------------------------
# UI
# --------------------------------------------------

if st.button("🚀 Run Extraction"):

    data = parse_all_pdfs()

    os.makedirs("data", exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    st.success("Extraction complete!")


# --------------------------------------------------
# Display Results
# --------------------------------------------------

if os.path.exists(OUTPUT_FILE):

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        cluster_data = json.load(f)

    df = pd.DataFrame(cluster_data)

    st.subheader("📊 Extracted Dataset")
    st.dataframe(df[["journal_name", "section_label", "word_count"]])

    st.subheader("📄 Preview")

    selected_row = st.selectbox("Select Row", df.index)
    st.text_area("Section Content", df.loc[selected_row, "text"], height=400)
