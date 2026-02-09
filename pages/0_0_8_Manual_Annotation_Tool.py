import streamlit as st
import os
import glob
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

DATA_ROOT = "data/ocr_pdf"
ANNOTATION_FILE = "data/manual_annotation_paper.json"

st.title("📝 Manual Annotation + Analysis Dashboard")

# ==========================================================
# LOAD ANNOTATION FILE
# ==========================================================

if os.path.exists(ANNOTATION_FILE):
    with open(ANNOTATION_FILE, "r", encoding="utf-8") as f:
        manual_annotations = json.load(f)
else:
    manual_annotations = {}

# ==========================================================
# SELECT PDF
# ==========================================================

pdf_folders = [
    d for d in os.listdir(DATA_ROOT)
    if os.path.isdir(os.path.join(DATA_ROOT, d))
]

selected_pdf = st.sidebar.selectbox("Select PDF Folder", pdf_folders)

# ==========================================================
# LOAD FULL TEXT
# ==========================================================

def read_all_pages(pdf_name):
    folder_path = os.path.join(DATA_ROOT, pdf_name, "pages")
    page_files = sorted(glob.glob(os.path.join(folder_path, "*.md")))

    full_text = ""
    for file in page_files:
        with open(file, "r", encoding="utf-8") as f:
            full_text += f.read() + "\n"

    return full_text


full_text = read_all_pages(selected_pdf)

if selected_pdf not in manual_annotations:
    manual_annotations[selected_pdf] = {}

# ==========================================================
# ANNOTATION TABLE
# ==========================================================

st.subheader("📋 Manual Annotation Table")

annotation_records = []

for label, text in manual_annotations[selected_pdf].items():
    annotation_records.append({
        "journal_name": selected_pdf,
        "section_label": label,
        "char_count": len(text),
        "word_count": len(re.findall(r"\b\w+\b", text))
    })

df_annotations = pd.DataFrame(annotation_records)

if not df_annotations.empty:
    st.dataframe(df_annotations)
else:
    st.info("No annotations yet.")

# ==========================================================
# ADD NEW ANNOTATION
# ==========================================================

st.subheader("➕ Add Annotation")

new_label = st.text_input("Section Label (e.g., Methodology)")
new_text = st.text_area("Paste Text Segment Here", height=200)

if st.button("Save Annotation"):

    if new_label and new_text:
        manual_annotations[selected_pdf][new_label] = new_text

        os.makedirs("data", exist_ok=True)

        with open(ANNOTATION_FILE, "w", encoding="utf-8") as f:
            json.dump(manual_annotations, f, indent=4)

        st.success("Annotation saved successfully!")

# ==========================================================
# ROBUST REMAINING TEXT (INDEX-BASED)
# ==========================================================

st.subheader("🧠 Remaining (Unannotated) Text")

annotated_ranges = []

for text in manual_annotations[selected_pdf].values():
    start_index = full_text.find(text)
    if start_index != -1:
        end_index = start_index + len(text)
        annotated_ranges.append((start_index, end_index))

annotated_ranges = sorted(annotated_ranges)

# Merge overlapping
merged_ranges = []
for start, end in annotated_ranges:
    if not merged_ranges:
        merged_ranges.append([start, end])
    else:
        prev_start, prev_end = merged_ranges[-1]
        if start <= prev_end:
            merged_ranges[-1][1] = max(prev_end, end)
        else:
            merged_ranges.append([start, end])

remaining_chunks = []
last_end = 0

for start, end in merged_ranges:
    if start > last_end:
        remaining_chunks.append(full_text[last_end:start])
    last_end = end

if last_end < len(full_text):
    remaining_chunks.append(full_text[last_end:])

remaining_text = "\n".join(remaining_chunks).strip()

coverage = 1 - (len(remaining_text) / len(full_text)) if len(full_text) > 0 else 0

st.metric("Annotation Coverage", f"{coverage:.2%}")

st.text_area("Remaining Text", remaining_text, height=350)

# ==========================================================
# CLUSTER MANUALLY ANNOTATED SECTIONS
# ==========================================================

if not df_annotations.empty:

    st.subheader("📊 Cluster Manual Sections")

    n_clusters = st.slider("Number of Clusters", 2, 8, 3)

    if st.button("Run Clustering"):

        text_data = [
            manual_annotations[selected_pdf][label]
            for label in manual_annotations[selected_pdf]
        ]

        vectorizer = TfidfVectorizer(stop_words="english", max_features=2000)
        X = vectorizer.fit_transform(text_data)

        model = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = model.fit_predict(X)

        df_cluster = pd.DataFrame({
            "section_label": list(manual_annotations[selected_pdf].keys()),
            "cluster": cluster_labels
        })

        st.dataframe(df_cluster)

        cluster_counts = df_cluster["cluster"].value_counts().sort_index()

        fig = plt.figure()
        plt.bar(cluster_counts.index.astype(str), cluster_counts.values)
        plt.xlabel("Cluster")
        plt.ylabel("Number of Sections")
        plt.title("Manual Section Cluster Distribution")

        st.pyplot(fig)


# import streamlit as st
# import os
# import glob
# import json

# DATA_ROOT = "data/ocr_pdf"
# ANNOTATION_FILE = "data/manual_annotation_paper.json"

# st.title("📝 Manual PDF Annotation Tool")

# # --------------------------------------------------
# # Load / Initialize Annotation JSON
# # --------------------------------------------------

# if os.path.exists(ANNOTATION_FILE):
#     with open(ANNOTATION_FILE, "r", encoding="utf-8") as f:
#         manual_annotations = json.load(f)
# else:
#     manual_annotations = {}

# # --------------------------------------------------
# # Select Any PDF Folder
# # --------------------------------------------------

# pdf_paths = [
#     os.path.join(DATA_ROOT, d)
#     for d in os.listdir(DATA_ROOT)
#     if os.path.isdir(os.path.join(DATA_ROOT, d))
# ]

# pdf_names = [os.path.basename(p) for p in pdf_paths]

# selected_pdf_name = st.sidebar.selectbox("Select PDF Folder", pdf_names)

# selected_pdf_path = os.path.join(DATA_ROOT, selected_pdf_name)

# # --------------------------------------------------
# # Load All Markdown Files
# # --------------------------------------------------

# def read_all_pages(folder_path):
#     pages_path = os.path.join(folder_path, "pages")
#     page_files = sorted(glob.glob(os.path.join(pages_path, "*.md")))

#     full_text = ""
#     for file in page_files:
#         with open(file, "r", encoding="utf-8") as f:
#             full_text += f.read() + "\n"

#     return full_text


# full_text = read_all_pages(selected_pdf_path)

# # --------------------------------------------------
# # Ensure PDF Key Exists
# # --------------------------------------------------

# if selected_pdf_name not in manual_annotations:
#     manual_annotations[selected_pdf_name] = {}

# # --------------------------------------------------
# # Show Existing Annotations
# # --------------------------------------------------

# st.subheader("📌 Existing Annotations")

# if manual_annotations[selected_pdf_name]:
#     for label, text in manual_annotations[selected_pdf_name].items():
#         st.markdown(f"**{label}** ({len(text)} chars)")
# else:
#     st.info("No annotations yet for this PDF.")

# # --------------------------------------------------
# # Add New Annotation
# # --------------------------------------------------

# st.subheader("➕ Add Annotation")

# new_label = st.text_input("Section Label (e.g., Methodology)")
# new_text = st.text_area("Paste Text Segment Here", height=200)

# if st.button("Save Annotation"):

#     if new_label and new_text:

#         manual_annotations[selected_pdf_name][new_label] = new_text

#         os.makedirs("data", exist_ok=True)

#         with open(ANNOTATION_FILE, "w", encoding="utf-8") as f:
#             json.dump(manual_annotations, f, indent=4)

#         st.success(f"Annotation saved for {selected_pdf_name}!")

# # --------------------------------------------------
# # Remaining Text Viewer
# # --------------------------------------------------

# st.subheader("🧠 Remaining (Unannotated) Text")

# remaining_text = full_text

# for text in manual_annotations[selected_pdf_name].values():
#     remaining_text = remaining_text.replace(text, "")

# remaining_text = remaining_text.strip()

# st.text_area("Remaining Text", remaining_text, height=400)
