import streamlit as st
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import re

DATA_DIR = "data/ocr_pdf"

st.title("📚 Journal Page Explorer")

# ------------------------
# Helper Functions
# ------------------------

def get_pdfs():
    return [
        d for d in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, d))
    ]

def get_pages(pdf_name):
    page_path = os.path.join(DATA_DIR, pdf_name, "pages")
    return sorted(glob.glob(os.path.join(page_path, "*.md")))

def read_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def compute_word_stats(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return words, len(words)

# ------------------------
# Sidebar Controls
# ------------------------

pdf_list = get_pdfs()
selected_pdf = st.sidebar.selectbox("Select Journal", pdf_list)

pages = get_pages(selected_pdf)

page_options = ["All Pages"] + [os.path.basename(p) for p in pages]
selected_page = st.sidebar.selectbox("Select Page", page_options)

viz_type = st.sidebar.selectbox(
    "Visualization",
    ["Word Count per Page", "Top Keywords", "Raw Markdown"]
)

# ------------------------
# Load Content
# ------------------------

page_texts = []
page_names = []

if selected_page == "All Pages":
    for p in pages:
        page_texts.append(read_markdown(p))
        page_names.append(os.path.basename(p))
else:
    selected_path = os.path.join(DATA_DIR, selected_pdf, "pages", selected_page)
    page_texts.append(read_markdown(selected_path))
    page_names.append(selected_page)

# ------------------------
# Visualization
# ------------------------

if viz_type == "Raw Markdown":
    st.subheader("📄 Markdown Content")
    st.markdown(page_texts[0])

elif viz_type == "Word Count per Page":
    st.subheader("📊 Word Count Distribution")

    word_counts = []
    for text in page_texts:
        _, count = compute_word_stats(text)
        word_counts.append(count)

    fig = plt.figure()
    plt.bar(page_names, word_counts)
    plt.xticks(rotation=90)
    plt.ylabel("Word Count")
    plt.title("Word Count per Page")

    st.pyplot(fig)

elif viz_type == "Top Keywords":
    st.subheader("🔎 Top Keywords")

    combined_text = " ".join(page_texts)
    words, _ = compute_word_stats(combined_text)

    stopwords = set([
        "the","and","of","to","in","a","for","is","on","that",
        "with","as","by","an","are","this","be","or","from"
    ])

    filtered = [w for w in words if w not in stopwords and len(w) > 3]

    counter = Counter(filtered)
    top_words = counter.most_common(20)

    df = pd.DataFrame(top_words, columns=["Word", "Frequency"])
    st.dataframe(df)

    fig = plt.figure()
    plt.bar(df["Word"], df["Frequency"])
    plt.xticks(rotation=90)
    plt.title("Top 20 Keywords")
    st.pyplot(fig)
