import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from bertopic import BERTopic
from umap import UMAP

# --------------------------------------------------
# Streamlit setup
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("📚 Journal Clustering & Topic Intelligence Dashboard")

# --------------------------------------------------
# Constants
# --------------------------------------------------
MISSING_VALUES = {
    "Abstract": "(missing abstract)",
    "Journal": "(missing journal)",
    "DOI": "(missing DOI)"
}

# --------------------------------------------------
# Data loading
# --------------------------------------------------
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

uploaded_file = st.file_uploader("Upload journal CSV", type=["csv"])
if not uploaded_file:
    st.stop()

df_raw = load_data(uploaded_file)

st.subheader("📄 Raw Dataset Preview")
st.dataframe(df_raw.head(), use_container_width=True)

# --------------------------------------------------
# Missing-value analysis
# --------------------------------------------------
st.header("🧹 Data Quality: Missing Placeholder Analysis")

missing_stats = []
for col, placeholder in MISSING_VALUES.items():
    if col in df_raw.columns:
        count = (df_raw[col] == placeholder).sum()
        missing_stats.append({
            "Column": col,
            "Placeholder": placeholder,
            "Count": count,
            "Percentage (%)": round(100 * count / len(df_raw), 2)
        })

missing_df = pd.DataFrame(missing_stats)
st.dataframe(missing_df, use_container_width=True)

fig, ax = plt.subplots()
ax.bar(missing_df["Column"], missing_df["Count"])
ax.set_title("Count of Placeholder Values per Column")
ax.set_ylabel("Number of rows")
st.pyplot(fig)

# --------------------------------------------------
# Cleaning step
# --------------------------------------------------
st.header("🧼 Data Cleaning")

df = df_raw.copy()

# Replace placeholders
if "Abstract" in df.columns:
    df["Abstract"] = df["Abstract"].replace(
        MISSING_VALUES["Abstract"], ""
    )

if "Journal" in df.columns:
    df["Journal"] = df["Journal"].replace(
        MISSING_VALUES["Journal"], "Unknown"
    )

if "DOI" in df.columns:
    df["DOI"] = df["DOI"].replace(
        MISSING_VALUES["DOI"], ""
    )

# Ensure required columns
required_cols = {"Title", "Journal", "Year"}
if not required_cols.issubset(df.columns):
    st.error("CSV must contain Title, Journal, and Year columns")
    st.stop()

df["Title"] = df["Title"].fillna("")
df["Journal"] = df["Journal"].fillna("Unknown")

# --------------------------------------------------
# ✅ SAFE YEAR HANDLING (INTEGRATED FIX)
# --------------------------------------------------
st.header("📅 Year Validation")

df["Year_raw"] = df["Year"]

df["Year"] = pd.to_numeric(
    df["Year"],
    errors="coerce"   # invalid strings → NaN
)

invalid_years = df["Year"].isna().sum()
st.info(f"Invalid or missing Year values detected: {invalid_years}")

df["Year"] = df["Year"].fillna(0).astype(int)

year_quality = pd.DataFrame({
    "Type": ["Valid Year", "Invalid / Missing"],
    "Count": [
        (df["Year"] > 0).sum(),
        (df["Year"] == 0).sum()
    ]
})

st.bar_chart(year_quality.set_index("Type"))

st.success(f"Cleaning complete — {len(df)} rows retained")

st.subheader("📄 Cleaned Dataset Preview")
st.dataframe(df.head(), use_container_width=True)

# --------------------------------------------------
# Text selection
# --------------------------------------------------
st.sidebar.header("⚙️ Settings")
text_source = st.sidebar.selectbox(
    "Text used for clustering",
    ["Title only", "Title + Abstract"]
)

if text_source == "Title + Abstract" and "Abstract" in df.columns:
    df["text"] = df["Title"] + ". " + df["Abstract"]
else:
    df["text"] = df["Title"]

documents = df["text"].tolist()

# --------------------------------------------------
# Embedding model
# --------------------------------------------------
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_embedding_model()

with st.spinner("🔎 Encoding documents..."):
    embeddings = model.encode(documents, show_progress_bar=False)

# ==================================================
# 🧪 TF-IDF vs Embedding Clustering
# ==================================================
st.header("🧪 TF-IDF vs Embedding Clustering")

k = st.slider("Number of clusters (KMeans)", 2, 20, 6)

tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
X_tfidf = tfidf.fit_transform(documents)

kmeans_tfidf = KMeans(n_clusters=k, random_state=42, n_init=10)
df["cluster_tfidf"] = kmeans_tfidf.fit_predict(X_tfidf)

kmeans_embed = KMeans(n_clusters=k, random_state=42, n_init=10)
df["cluster_embed"] = kmeans_embed.fit_predict(embeddings)

col1, col2 = st.columns(2)
with col1:
    st.subheader("TF-IDF Clusters")
    st.bar_chart(df["cluster_tfidf"].value_counts().sort_index())

with col2:
    st.subheader("Embedding Clusters")
    st.bar_chart(df["cluster_embed"].value_counts().sort_index())

# --------------------------------------------------
# PCA visualization
# --------------------------------------------------
pca = PCA(n_components=2)
coords = pca.fit_transform(embeddings)

fig, ax = plt.subplots()
ax.scatter(
    coords[:, 0],
    coords[:, 1],
    c=df["cluster_embed"],
    cmap="tab10",
    alpha=0.7
)
ax.set_title("Embedding-Based Clusters (PCA)")
st.pyplot(fig)

# ==================================================
# 🔁 BERTopic
# ==================================================
st.header("🔁 BERTopic Semantic Topic Modeling")

with st.spinner("Training BERTopic..."):
    umap_model = UMAP(
        n_neighbors=15,
        n_components=5,
        min_dist=0.0,
        metric="cosine"
    )

    topic_model = BERTopic(
        embedding_model=model,
        umap_model=umap_model,
        calculate_probabilities=True,
        verbose=False
    )

    topics, probs = topic_model.fit_transform(documents)

df["bertopic_topic"] = topics

st.subheader("📌 Topic Overview")
st.dataframe(
    topic_model.get_topic_info(),
    use_container_width=True
)

# ==================================================
# 📈 Topic Evolution Over Time
# ==================================================
st.header("📈 Topic Evolution Over Time")

df_year_valid = df[df["Year"] > 0]

topic_over_time = (
    df_year_valid[df_year_valid["bertopic_topic"] >= 0]
    .groupby(["Year", "bertopic_topic"])
    .size()
    .reset_index(name="count")
)

selected_topic = st.selectbox(
    "Select topic",
    sorted(topic_over_time["bertopic_topic"].unique())
)

timeline = topic_over_time[
    topic_over_time["bertopic_topic"] == selected_topic
]

st.line_chart(timeline.set_index("Year")["count"])

# ==================================================
# 🧭 Journal-Level Clustering
# ==================================================
st.header("🧭 Journal-Level Clustering")

journal_group = (
    df.groupby("Journal")["text"]
    .apply(lambda x: " ".join(x))
    .reset_index()
)

with st.spinner("Encoding journals..."):
    journal_embeddings = model.encode(journal_group["text"].tolist())

k_journal = st.slider("Journal clusters", 2, 10, 4)

journal_kmeans = KMeans(
    n_clusters=k_journal,
    random_state=42,
    n_init=10
)

journal_group["journal_cluster"] = journal_kmeans.fit_predict(journal_embeddings)

st.dataframe(
    journal_group[["Journal", "journal_cluster"]],
    use_container_width=True
)

# --------------------------------------------------
# Export
# --------------------------------------------------
st.header("📤 Export Results")

csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download clustered CSV",
    csv,
    "clustered_journals_cleaned.csv",
    "text/csv"
)


# import streamlit as st
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt

# from sentence_transformers import SentenceTransformer
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cluster import KMeans
# from sklearn.decomposition import PCA

# from bertopic import BERTopic
# from umap import UMAP

# # --------------------------------------------------
# # Streamlit setup
# # --------------------------------------------------
# st.set_page_config(layout="wide")
# st.title("📚 Journal Clustering & Topic Intelligence Dashboard")

# # --------------------------------------------------
# # Constants
# # --------------------------------------------------
# MISSING_VALUES = {
#     "Abstract": "(missing abstract)",
#     "Journal": "(missing journal)",
#     "DOI": "(missing DOI)"
# }

# # --------------------------------------------------
# # Data loading
# # --------------------------------------------------
# @st.cache_data
# def load_data(file):
#     return pd.read_csv(file)

# uploaded_file = st.file_uploader("Upload journal CSV", type=["csv"])
# if not uploaded_file:
#     st.stop()

# df_raw = load_data(uploaded_file)

# st.subheader("📄 Raw Dataset Preview")
# st.dataframe(df_raw.head(), use_container_width=True)

# # --------------------------------------------------
# # Missing-value analysis
# # --------------------------------------------------
# st.header("🧹 Data Quality: Missing Placeholder Analysis")

# missing_stats = []

# for col, placeholder in MISSING_VALUES.items():
#     if col in df_raw.columns:
#         count = (df_raw[col] == placeholder).sum()
#         missing_stats.append({
#             "Column": col,
#             "Placeholder": placeholder,
#             "Count": count,
#             "Percentage (%)": round(100 * count / len(df_raw), 2)
#         })

# missing_df = pd.DataFrame(missing_stats)
# st.dataframe(missing_df, use_container_width=True)

# # --------------------------------------------------
# # Visualization
# # --------------------------------------------------
# fig, ax = plt.subplots()
# ax.bar(
#     missing_df["Column"],
#     missing_df["Count"]
# )
# ax.set_title("Count of Placeholder Values per Column")
# ax.set_ylabel("Number of rows")
# st.pyplot(fig)

# # --------------------------------------------------
# # Cleaning step
# # --------------------------------------------------
# st.header("🧼 Data Cleaning")

# df = df_raw.copy()

# # Replace placeholders
# if "Abstract" in df.columns:
#     df["Abstract"] = df["Abstract"].replace(
#         MISSING_VALUES["Abstract"], ""
#     )

# if "Journal" in df.columns:
#     df["Journal"] = df["Journal"].replace(
#         MISSING_VALUES["Journal"], "Unknown"
#     )

# if "DOI" in df.columns:
#     df["DOI"] = df["DOI"].replace(
#         MISSING_VALUES["DOI"], ""
#     )

# # Ensure required columns
# required_cols = {"Title", "Journal", "Year"}
# if not required_cols.issubset(df.columns):
#     st.error("CSV must contain Title, Journal, and Year columns")
#     st.stop()

# df["Title"] = df["Title"].fillna("")
# df["Journal"] = df["Journal"].fillna("Unknown")
# df["Year"] = df["Year"].fillna(0).astype(int)

# st.success(f"Cleaning complete — {len(df)} rows retained")

# st.subheader("📄 Cleaned Dataset Preview")
# st.dataframe(df.head(), use_container_width=True)

# # --------------------------------------------------
# # Text selection
# # --------------------------------------------------
# st.sidebar.header("⚙️ Settings")
# text_source = st.sidebar.selectbox(
#     "Text used for clustering",
#     ["Title only", "Title + Abstract"]
# )

# if text_source == "Title + Abstract" and "Abstract" in df.columns:
#     df["text"] = df["Title"] + ". " + df["Abstract"]
# else:
#     df["text"] = df["Title"]

# documents = df["text"].tolist()

# # --------------------------------------------------
# # Embedding model
# # --------------------------------------------------
# @st.cache_resource
# def load_embedding_model():
#     return SentenceTransformer("all-MiniLM-L6-v2")

# model = load_embedding_model()

# with st.spinner("🔎 Encoding documents..."):
#     embeddings = model.encode(documents, show_progress_bar=False)

# # ==================================================
# # 🧪 TF-IDF vs Embedding Clustering
# # ==================================================
# st.header("🧪 TF-IDF vs Embedding Clustering")

# k = st.slider("Number of clusters (KMeans)", 2, 20, 6)

# tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
# X_tfidf = tfidf.fit_transform(documents)

# kmeans_tfidf = KMeans(n_clusters=k, random_state=42, n_init=10)
# df["cluster_tfidf"] = kmeans_tfidf.fit_predict(X_tfidf)

# kmeans_embed = KMeans(n_clusters=k, random_state=42, n_init=10)
# df["cluster_embed"] = kmeans_embed.fit_predict(embeddings)

# col1, col2 = st.columns(2)
# with col1:
#     st.subheader("TF-IDF Clusters")
#     st.bar_chart(df["cluster_tfidf"].value_counts().sort_index())

# with col2:
#     st.subheader("Embedding Clusters")
#     st.bar_chart(df["cluster_embed"].value_counts().sort_index())

# # --------------------------------------------------
# # PCA visualization
# # --------------------------------------------------
# pca = PCA(n_components=2)
# coords = pca.fit_transform(embeddings)

# fig, ax = plt.subplots()
# ax.scatter(
#     coords[:, 0],
#     coords[:, 1],
#     c=df["cluster_embed"],
#     cmap="tab10",
#     alpha=0.7
# )
# ax.set_title("Embedding-Based Clusters (PCA)")
# st.pyplot(fig)

# # ==================================================
# # 🔁 BERTopic
# # ==================================================
# st.header("🔁 BERTopic Semantic Topic Modeling")

# with st.spinner("Training BERTopic..."):
#     umap_model = UMAP(
#         n_neighbors=15,
#         n_components=5,
#         min_dist=0.0,
#         metric="cosine"
#     )

#     topic_model = BERTopic(
#         embedding_model=model,
#         umap_model=umap_model,
#         calculate_probabilities=True,
#         verbose=False
#     )

#     topics, probs = topic_model.fit_transform(documents)

# df["bertopic_topic"] = topics

# st.subheader("📌 Topic Overview")
# st.dataframe(
#     topic_model.get_topic_info(),
#     use_container_width=True
# )

# # ==================================================
# # 📈 Topic Evolution Over Time
# # ==================================================
# st.header("📈 Topic Evolution Over Time")

# topic_over_time = (
#     df[df["bertopic_topic"] >= 0]
#     .groupby(["Year", "bertopic_topic"])
#     .size()
#     .reset_index(name="count")
# )

# selected_topic = st.selectbox(
#     "Select topic",
#     sorted(topic_over_time["bertopic_topic"].unique())
# )

# timeline = topic_over_time[
#     topic_over_time["bertopic_topic"] == selected_topic
# ]

# st.line_chart(timeline.set_index("Year")["count"])

# # ==================================================
# # 🧭 Journal-Level Clustering
# # ==================================================
# st.header("🧭 Journal-Level Clustering")

# journal_group = (
#     df.groupby("Journal")["text"]
#     .apply(lambda x: " ".join(x))
#     .reset_index()
# )

# with st.spinner("Encoding journals..."):
#     journal_embeddings = model.encode(journal_group["text"].tolist())

# k_journal = st.slider("Journal clusters", 2, 10, 4)

# journal_kmeans = KMeans(
#     n_clusters=k_journal,
#     random_state=42,
#     n_init=10
# )

# journal_group["journal_cluster"] = journal_kmeans.fit_predict(journal_embeddings)

# st.dataframe(
#     journal_group[["Journal", "journal_cluster"]],
#     use_container_width=True
# )

# # --------------------------------------------------
# # Export
# # --------------------------------------------------
# st.header("📤 Export Results")

# csv = df.to_csv(index=False).encode("utf-8")
# st.download_button(
#     "Download clustered CSV",
#     csv,
#     "clustered_journals_cleaned.csv",
#     "text/csv"
# )
