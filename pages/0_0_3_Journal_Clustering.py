import streamlit as st
import os
import glob
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

DATA_DIR = "data/ocr_pdf"
OUTPUT_FILE = "data/cluster_journal_text.json"

st.title("🧠 Journal Section Clustering Dashboard")

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


def extract_section(text, section_keywords):
    pattern = r"(#.+?)\n"
    headers = [(m.start(), m.group()) for m in re.finditer(pattern, text)]

    for i, (pos, header) in enumerate(headers):
        header_lower = header.lower()

        if any(keyword in header_lower for keyword in section_keywords):
            start = pos
            end = headers[i + 1][0] if i + 1 < len(headers) else len(text)
            return text[start:end].strip()

    return ""


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

        abstract = extract_section(full_text, ["abstract"])
        introduction = extract_section(full_text, ["introduction"])
        literature_review = extract_section(full_text, ["literature review"])

        cluster_data.append({
            "journal_name": journal_name,
            "abstract": abstract,
            "introduction": introduction,
            "literature_review": literature_review
        })

    return cluster_data


# --------------------------------------------------
# UI Buttons
# --------------------------------------------------

if st.button("🔄 Parse All Journals"):

    data = parse_all_pdfs()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    st.success("Cluster text saved to JSON!")

# --------------------------------------------------
# Load Existing JSON
# --------------------------------------------------

if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        cluster_data = json.load(f)

    df = pd.DataFrame(cluster_data)

    st.subheader("📋 Parsed Journal Sections")
    st.dataframe(df)

    # --------------------------------------------------
    # Clustering Section
    # --------------------------------------------------

    st.subheader("📊 Cluster Journals")

    n_clusters = st.slider("Number of Clusters", 2, 10, 3)

    if st.button("🚀 Run Clustering"):

        text_data = (
            df["introduction"].fillna("") +
            " " +
            df["literature_review"].fillna("")
        )

        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=2000
        )

        X = vectorizer.fit_transform(text_data)

        model = KMeans(n_clusters=n_clusters, random_state=42)
        df["cluster"] = model.fit_predict(X)

        st.dataframe(df[["journal_name", "cluster"]])

        # --------------------------------------------------
        # Visualization
        # --------------------------------------------------

        cluster_counts = df["cluster"].value_counts().sort_index()

        fig = plt.figure()
        plt.bar(cluster_counts.index.astype(str), cluster_counts.values)
        plt.xlabel("Cluster")
        plt.ylabel("Number of Journals")
        plt.title("Journal Cluster Distribution")

        st.pyplot(fig)

else:
    st.info("No cluster JSON found. Click 'Parse All Journals' first.")


# import streamlit as st
# import os
# import glob
# import pandas as pd
# import matplotlib.pyplot as plt
# from collections import Counter
# import re

# DATA_DIR = "data/ocr_pdf"

# st.title("📚 Journal Page Explorer")

# # ------------------------
# # Helper Functions
# # ------------------------

# def get_pdfs():
#     return [
#         d for d in os.listdir(DATA_DIR)
#         if os.path.isdir(os.path.join(DATA_DIR, d))
#     ]

# def get_pages(pdf_name):
#     page_path = os.path.join(DATA_DIR, pdf_name, "pages")
#     return sorted(glob.glob(os.path.join(page_path, "*.md")))

# def read_markdown(file_path):
#     with open(file_path, "r", encoding="utf-8") as f:
#         return f.read()

# def compute_word_stats(text):
#     words = re.findall(r'\b\w+\b', text.lower())
#     return words, len(words)

# # ------------------------
# # Sidebar Controls
# # ------------------------

# pdf_list = get_pdfs()
# selected_pdf = st.sidebar.selectbox("Select Journal", pdf_list)

# pages = get_pages(selected_pdf)

# page_options = ["All Pages"] + [os.path.basename(p) for p in pages]
# selected_page = st.sidebar.selectbox("Select Page", page_options)

# viz_type = st.sidebar.selectbox(
#     "Visualization",
#     ["Word Count per Page", "Top Keywords", "Raw Markdown"]
# )

# # ------------------------
# # Load Content
# # ------------------------

# page_texts = []
# page_names = []

# if selected_page == "All Pages":
#     for p in pages:
#         page_texts.append(read_markdown(p))
#         page_names.append(os.path.basename(p))
# else:
#     selected_path = os.path.join(DATA_DIR, selected_pdf, "pages", selected_page)
#     page_texts.append(read_markdown(selected_path))
#     page_names.append(selected_page)

# # ------------------------
# # Visualization
# # ------------------------

# if viz_type == "Raw Markdown":
#     st.subheader("📄 Markdown Content")
#     st.markdown(page_texts[0])

# elif viz_type == "Word Count per Page":
#     st.subheader("📊 Word Count Distribution")

#     word_counts = []
#     for text in page_texts:
#         _, count = compute_word_stats(text)
#         word_counts.append(count)

#     fig = plt.figure()
#     plt.bar(page_names, word_counts)
#     plt.xticks(rotation=90)
#     plt.ylabel("Word Count")
#     plt.title("Word Count per Page")

#     st.pyplot(fig)

# elif viz_type == "Top Keywords":
#     st.subheader("🔎 Top Keywords")

#     combined_text = " ".join(page_texts)
#     words, _ = compute_word_stats(combined_text)

#     stopwords = set([
#         "the","and","of","to","in","a","for","is","on","that",
#         "with","as","by","an","are","this","be","or","from"
#     ])

#     filtered = [w for w in words if w not in stopwords and len(w) > 3]

#     counter = Counter(filtered)
#     top_words = counter.most_common(20)

#     df = pd.DataFrame(top_words, columns=["Word", "Frequency"])
#     st.dataframe(df)

#     fig = plt.figure()
#     plt.bar(df["Word"], df["Frequency"])
#     plt.xticks(rotation=90)
#     plt.title("Top 20 Keywords")
#     st.pyplot(fig)
