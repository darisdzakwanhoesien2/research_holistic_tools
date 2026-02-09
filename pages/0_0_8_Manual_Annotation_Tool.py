import streamlit as st
import os
import glob
import json

DATA_ROOT = "data/ocr_pdf"
ANNOTATION_FILE = "data/manual_annotation_paper.json"

st.title("📝 Manual PDF Annotation Tool")

# --------------------------------------------------
# Load / Initialize Annotation JSON
# --------------------------------------------------

if os.path.exists(ANNOTATION_FILE):
    with open(ANNOTATION_FILE, "r", encoding="utf-8") as f:
        manual_annotations = json.load(f)
else:
    manual_annotations = {}

# --------------------------------------------------
# Select Any PDF Folder
# --------------------------------------------------

pdf_paths = [
    os.path.join(DATA_ROOT, d)
    for d in os.listdir(DATA_ROOT)
    if os.path.isdir(os.path.join(DATA_ROOT, d))
]

pdf_names = [os.path.basename(p) for p in pdf_paths]

selected_pdf_name = st.sidebar.selectbox("Select PDF Folder", pdf_names)

selected_pdf_path = os.path.join(DATA_ROOT, selected_pdf_name)

# --------------------------------------------------
# Load All Markdown Files
# --------------------------------------------------

def read_all_pages(folder_path):
    pages_path = os.path.join(folder_path, "pages")
    page_files = sorted(glob.glob(os.path.join(pages_path, "*.md")))

    full_text = ""
    for file in page_files:
        with open(file, "r", encoding="utf-8") as f:
            full_text += f.read() + "\n"

    return full_text


full_text = read_all_pages(selected_pdf_path)

# --------------------------------------------------
# Ensure PDF Key Exists
# --------------------------------------------------

if selected_pdf_name not in manual_annotations:
    manual_annotations[selected_pdf_name] = {}

# --------------------------------------------------
# Show Existing Annotations
# --------------------------------------------------

st.subheader("📌 Existing Annotations")

if manual_annotations[selected_pdf_name]:
    for label, text in manual_annotations[selected_pdf_name].items():
        st.markdown(f"**{label}** ({len(text)} chars)")
else:
    st.info("No annotations yet for this PDF.")

# --------------------------------------------------
# Add New Annotation
# --------------------------------------------------

st.subheader("➕ Add Annotation")

new_label = st.text_input("Section Label (e.g., Methodology)")
new_text = st.text_area("Paste Text Segment Here", height=200)

if st.button("Save Annotation"):

    if new_label and new_text:

        manual_annotations[selected_pdf_name][new_label] = new_text

        os.makedirs("data", exist_ok=True)

        with open(ANNOTATION_FILE, "w", encoding="utf-8") as f:
            json.dump(manual_annotations, f, indent=4)

        st.success(f"Annotation saved for {selected_pdf_name}!")

# --------------------------------------------------
# Remaining Text Viewer
# --------------------------------------------------

st.subheader("🧠 Remaining (Unannotated) Text")

remaining_text = full_text

for text in manual_annotations[selected_pdf_name].values():
    remaining_text = remaining_text.replace(text, "")

remaining_text = remaining_text.strip()

st.text_area("Remaining Text", remaining_text, height=400)
