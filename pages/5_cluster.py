import streamlit as st
import pandas as pd
import json
import re

# --------------------------------------------------
# Streamlit setup
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("🧭 Dictionary-Based Journal Clustering")

# --------------------------------------------------
# Session state for refresh control
# --------------------------------------------------
if "cluster_version" not in st.session_state:
    st.session_state.cluster_version = 0

# --------------------------------------------------
# Sidebar: refresh control
# --------------------------------------------------
st.sidebar.header("📘 Cluster Dictionary")

if st.sidebar.button("🔄 Refresh cluster.json"):
    st.session_state.cluster_version += 1
    st.sidebar.success("Cluster dictionary reloaded")

st.sidebar.caption(f"Loaded version: {st.session_state.cluster_version}")

# --------------------------------------------------
# Load cluster dictionary
# --------------------------------------------------
@st.cache_data
def load_clusters(path="data/cluster.json", version=0):
    with open(path, "r") as f:
        return json.load(f)

clusters = load_clusters(version=st.session_state.cluster_version)
st.sidebar.json(clusters)

# --------------------------------------------------
# Load dataset
# --------------------------------------------------
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

uploaded_file = st.file_uploader("Upload journal CSV", type=["csv"])
if not uploaded_file:
    st.stop()

df = load_data(uploaded_file)

# --------------------------------------------------
# Preserve original schema
# --------------------------------------------------
EXPECTED_COLUMNS = [
    "DOI", "Title", "Authors", "Journal", "Year", "Abstract",
    "LitmapsId", "Cited By", "References", "PubMedId", "Tags"
]

for col in EXPECTED_COLUMNS:
    if col not in df.columns:
        df[col] = ""

# --------------------------------------------------
# Basic cleaning (non-destructive)
# --------------------------------------------------
df["Title"] = df["Title"].fillna("")
df["Abstract"] = df["Abstract"].fillna("")
df["Journal"] = df["Journal"].fillna("Unknown")

df["Title_raw"] = df["Title"]
df["Abstract_raw"] = df["Abstract"]

# --------------------------------------------------
# Text selection
# --------------------------------------------------
text_source = st.sidebar.selectbox(
    "Text used for matching",
    ["Title only", "Title + Abstract"]
)

if text_source == "Title + Abstract":
    df["text"] = (df["Title"] + " " + df["Abstract"]).str.lower()
else:
    df["text"] = df["Title"].str.lower()

# --------------------------------------------------
# Keyword matching
# --------------------------------------------------
def score_text_against_clusters(text, cluster_dict):
    scores = {}
    matches = {}

    for cluster, keywords in cluster_dict.items():
        found = []
        score = 0
        for kw in keywords:
            pattern = r"\b" + re.escape(kw.lower()) + r"\b"
            if re.search(pattern, text):
                found.append(kw)
                score += 1
        scores[cluster] = score
        matches[cluster] = found

    return scores, matches

# --------------------------------------------------
# Apply clustering
# --------------------------------------------------
labels, scores_out, matches_out = [], [], []

for text in df["text"]:
    scores, matches = score_text_against_clusters(text, clusters)
    best = max(scores, key=scores.get)

    if scores[best] == 0:
        labels.append("Unclassified")
        scores_out.append(0)
        matches_out.append([])
    else:
        labels.append(best)
        scores_out.append(scores[best])
        matches_out.append(matches[best])

df["dict_cluster"] = labels
df["dict_cluster_score"] = scores_out
df["matched_keywords"] = matches_out

# --------------------------------------------------
# Cluster distribution
# --------------------------------------------------
st.header("📊 Cluster Distribution")
st.bar_chart(df["dict_cluster"].value_counts())

# --------------------------------------------------
# Inspect cluster
# --------------------------------------------------
st.header("🔍 Inspect Cluster")

selected_cluster = st.selectbox(
    "Select cluster",
    sorted(df["dict_cluster"].unique())
)

subset = df[df["dict_cluster"] == selected_cluster]

st.write(f"**Papers in {selected_cluster}: {len(subset)}**")

st.dataframe(
    subset[
        ["Title", "Journal", "dict_cluster_score", "matched_keywords"]
    ],
    use_container_width=True
)

# --------------------------------------------------
# Paper-level inspector
# --------------------------------------------------
st.subheader("📄 Paper Inspector (Original Text)")

if len(subset) > 0:
    idx = st.selectbox(
        "Select a paper",
        subset.index,
        format_func=lambda i: subset.loc[i, "Title"]
    )

    paper = subset.loc[idx]

    def highlight(text, keywords):
        for kw in keywords:
            text = re.sub(
                rf"({re.escape(kw)})",
                r"**\1**",
                text,
                flags=re.IGNORECASE
            )
        return text

    st.markdown("### 🧾 Original Title")
    st.markdown(highlight(paper["Title_raw"], paper["matched_keywords"]))

    if paper["Abstract_raw"]:
        st.markdown("### 📄 Original Abstract")
        st.markdown(highlight(paper["Abstract_raw"], paper["matched_keywords"]))
    else:
        st.info("No abstract available.")

# --------------------------------------------------
# Export by cluster (REQUESTED FEATURE)
# --------------------------------------------------
st.header("📤 Export Clustered Data")

export_cluster = st.selectbox(
    "Select cluster to export",
    sorted(df["dict_cluster"].unique())
)

export_df = df[df["dict_cluster"] == export_cluster][EXPECTED_COLUMNS]

st.write(f"Rows to export: {len(export_df)}")

csv = export_df.to_csv(index=False).encode("utf-8")

st.download_button(
    f"Download {export_cluster} cluster CSV",
    csv,
    f"{export_cluster.lower()}_cluster.csv",
    "text/csv"
)


# import streamlit as st
# import pandas as pd
# import json
# import re
# import matplotlib.pyplot as plt

# # --------------------------------------------------
# # Streamlit setup
# # --------------------------------------------------
# st.set_page_config(layout="wide")
# st.title("🧭 Dictionary-Based Journal Clustering")

# # --------------------------------------------------
# # Session state for refresh control
# # --------------------------------------------------
# if "cluster_version" not in st.session_state:
#     st.session_state.cluster_version = 0

# # --------------------------------------------------
# # Sidebar: refresh control
# # --------------------------------------------------
# st.sidebar.header("📘 Cluster Dictionary")

# if st.sidebar.button("🔄 Refresh cluster.json"):
#     st.session_state.cluster_version += 1
#     st.sidebar.success("Cluster dictionary reloaded")

# st.sidebar.caption(
#     f"Loaded version: {st.session_state.cluster_version}"
# )

# # --------------------------------------------------
# # Load cluster dictionary (cached, versioned)
# # --------------------------------------------------
# @st.cache_data
# def load_clusters(path="data/cluster.json", version=0):
#     with open(path, "r") as f:
#         return json.load(f)

# clusters = load_clusters(version=st.session_state.cluster_version)

# st.sidebar.json(clusters)

# # --------------------------------------------------
# # Load dataset
# # --------------------------------------------------
# @st.cache_data
# def load_data(file):
#     return pd.read_csv(file)

# uploaded_file = st.file_uploader(
#     "Upload journal CSV",
#     type=["csv"]
# )

# if not uploaded_file:
#     st.stop()

# df = load_data(uploaded_file)

# # --------------------------------------------------
# # Basic cleaning (SAFE)
# # --------------------------------------------------
# df["Title"] = df.get("Title", "").fillna("")
# df["Abstract"] = df.get("Abstract", "").fillna("")
# df["Journal"] = df.get("Journal", "Unknown").fillna("Unknown")

# # Preserve original text for inspection
# df["Title_raw"] = df["Title"]
# df["Abstract_raw"] = df["Abstract"]

# # --------------------------------------------------
# # Text selection
# # --------------------------------------------------
# text_source = st.sidebar.selectbox(
#     "Text used for matching",
#     ["Title only", "Title + Abstract"]
# )

# if text_source == "Title + Abstract":
#     df["text"] = (df["Title"] + " " + df["Abstract"]).str.lower()
# else:
#     df["text"] = df["Title"].str.lower()

# # --------------------------------------------------
# # Keyword matching logic
# # --------------------------------------------------
# def score_text_against_clusters(text, cluster_dict):
#     scores = {}
#     matches = {}

#     for cluster, keywords in cluster_dict.items():
#         found = []
#         score = 0

#         for kw in keywords:
#             pattern = r"\b" + re.escape(kw.lower()) + r"\b"
#             if re.search(pattern, text):
#                 found.append(kw)
#                 score += 1

#         scores[cluster] = score
#         matches[cluster] = found

#     return scores, matches

# # --------------------------------------------------
# # Apply dictionary clustering
# # --------------------------------------------------
# labels = []
# scores_out = []
# matches_out = []

# for text in df["text"]:
#     scores, matches = score_text_against_clusters(text, clusters)
#     best_cluster = max(scores, key=scores.get)

#     if scores[best_cluster] == 0:
#         labels.append("Unclassified")
#         scores_out.append(0)
#         matches_out.append([])
#     else:
#         labels.append(best_cluster)
#         scores_out.append(scores[best_cluster])
#         matches_out.append(matches[best_cluster])

# df["dict_cluster"] = labels
# df["dict_cluster_score"] = scores_out
# df["matched_keywords"] = matches_out

# # --------------------------------------------------
# # Cluster distribution
# # --------------------------------------------------
# st.header("📊 Cluster Distribution")

# dist = df["dict_cluster"].value_counts()
# st.bar_chart(dist)

# # --------------------------------------------------
# # Inspect cluster (OVERVIEW + ORIGINAL PAPER VIEW)
# # --------------------------------------------------
# st.header("🔍 Inspect Cluster")

# selected_cluster = st.selectbox(
#     "Select cluster",
#     sorted(df["dict_cluster"].unique())
# )

# subset = df[df["dict_cluster"] == selected_cluster]

# st.write(f"**Papers in {selected_cluster}: {len(subset)}**")

# # ---- Overview table ----
# st.subheader("📋 Cluster Overview")

# st.dataframe(
#     subset[
#         ["Title", "Journal", "dict_cluster_score", "matched_keywords"]
#     ],
#     use_container_width=True
# )

# # ---- Paper-level inspector ----
# st.subheader("📄 Paper Inspector (Original Text)")

# if len(subset) == 0:
#     st.info("No papers in this cluster.")
# else:
#     paper_index = st.selectbox(
#         "Select a paper",
#         subset.index,
#         format_func=lambda i: subset.loc[i, "Title"]
#     )

#     paper = subset.loc[paper_index]

#     # Keyword highlighting helper
#     def highlight_keywords(text, keywords):
#         highlighted = text
#         for kw in keywords:
#             pattern = re.compile(rf"({re.escape(kw)})", re.IGNORECASE)
#             highlighted = pattern.sub(r"**\\1**", highlighted)
#         return highlighted

#     st.markdown("### 🏷️ Metadata")
#     st.write(f"**Journal:** {paper['Journal']}")
#     st.write(f"**Cluster:** {paper['dict_cluster']}")
#     st.write(f"**Cluster score:** {paper['dict_cluster_score']}")
#     st.write(f"**Matched keywords:** {paper['matched_keywords']}")

#     st.markdown("### 🧾 Original Title")
#     st.markdown(
#         highlight_keywords(
#             paper["Title_raw"],
#             paper["matched_keywords"]
#         )
#     )

#     if paper["Abstract_raw"]:
#         st.markdown("### 📄 Original Abstract")
#         st.markdown(
#             highlight_keywords(
#                 paper["Abstract_raw"],
#                 paper["matched_keywords"]
#             )
#         )
#     else:
#         st.info("No abstract available.")

# # --------------------------------------------------
# # Confidence filtering
# # --------------------------------------------------
# st.header("🎯 Confidence Filtering")

# min_score = st.slider(
#     "Minimum keyword matches",
#     min_value=1,
#     max_value=5,
#     value=1
# )

# filtered = df[df["dict_cluster_score"] >= min_score]

# st.write(f"Papers with score ≥ {min_score}: {len(filtered)}")

# st.dataframe(
#     filtered[
#         ["Title", "dict_cluster", "dict_cluster_score"]
#     ],
#     use_container_width=True
# )

# # --------------------------------------------------
# # Export results
# # --------------------------------------------------
# st.header("📤 Export Results")

# csv = df.to_csv(index=False).encode("utf-8")

# st.download_button(
#     "Download dictionary-clustered CSV",
#     csv,
#     "dictionary_clustered_journals.csv",
#     "text/csv"
# )


# import streamlit as st
# import pandas as pd
# import json
# import re
# import matplotlib.pyplot as plt

# # --------------------------------------------------
# # Streamlit setup
# # --------------------------------------------------
# st.set_page_config(layout="wide")
# st.title("🧭 Dictionary-Based Journal Clustering")

# # --------------------------------------------------
# # Session state for refresh control
# # --------------------------------------------------
# if "cluster_version" not in st.session_state:
#     st.session_state.cluster_version = 0

# # --------------------------------------------------
# # Sidebar: refresh control
# # --------------------------------------------------
# st.sidebar.header("📘 Cluster Dictionary")

# if st.sidebar.button("🔄 Refresh cluster.json"):
#     st.session_state.cluster_version += 1
#     st.sidebar.success("Cluster dictionary reloaded")

# st.sidebar.caption(
#     f"Loaded version: {st.session_state.cluster_version}"
# )

# # --------------------------------------------------
# # Load cluster dictionary (cached, versioned)
# # --------------------------------------------------
# @st.cache_data
# def load_clusters(path="data/cluster.json", version=0):
#     with open(path, "r") as f:
#         return json.load(f)

# clusters = load_clusters(
#     version=st.session_state.cluster_version
# )

# st.sidebar.json(clusters)

# # --------------------------------------------------
# # Load dataset
# # --------------------------------------------------
# @st.cache_data
# def load_data(file):
#     return pd.read_csv(file)

# uploaded_file = st.file_uploader(
#     "Upload journal CSV",
#     type=["csv"]
# )

# if not uploaded_file:
#     st.stop()

# df = load_data(uploaded_file)

# # --------------------------------------------------
# # Basic cleaning
# # --------------------------------------------------
# df["Title"] = df.get("Title", "").fillna("")
# df["Abstract"] = df.get("Abstract", "").fillna("")
# df["Journal"] = df.get("Journal", "Unknown").fillna("Unknown")

# # --------------------------------------------------
# # Text selection
# # --------------------------------------------------
# text_source = st.sidebar.selectbox(
#     "Text used for matching",
#     ["Title only", "Title + Abstract"]
# )

# if text_source == "Title + Abstract":
#     df["text"] = (df["Title"] + " " + df["Abstract"]).str.lower()
# else:
#     df["text"] = df["Title"].str.lower()

# # --------------------------------------------------
# # Keyword matching logic
# # --------------------------------------------------
# def score_text_against_clusters(text, cluster_dict):
#     scores = {}
#     matches = {}

#     for cluster, keywords in cluster_dict.items():
#         found = []
#         score = 0

#         for kw in keywords:
#             pattern = r"\b" + re.escape(kw.lower()) + r"\b"
#             if re.search(pattern, text):
#                 found.append(kw)
#                 score += 1

#         scores[cluster] = score
#         matches[cluster] = found

#     return scores, matches

# # --------------------------------------------------
# # Apply dictionary clustering
# # --------------------------------------------------
# labels = []
# scores_out = []
# matches_out = []

# for text in df["text"]:
#     scores, matches = score_text_against_clusters(text, clusters)
#     best_cluster = max(scores, key=scores.get)

#     if scores[best_cluster] == 0:
#         labels.append("Unclassified")
#         scores_out.append(0)
#         matches_out.append([])
#     else:
#         labels.append(best_cluster)
#         scores_out.append(scores[best_cluster])
#         matches_out.append(matches[best_cluster])

# df["dict_cluster"] = labels
# df["dict_cluster_score"] = scores_out
# df["matched_keywords"] = matches_out

# # --------------------------------------------------
# # Cluster distribution
# # --------------------------------------------------
# st.header("📊 Cluster Distribution")

# dist = df["dict_cluster"].value_counts()
# st.bar_chart(dist)

# # --------------------------------------------------
# # Inspect cluster
# # --------------------------------------------------
# st.header("🔍 Inspect Cluster")

# selected_cluster = st.selectbox(
#     "Select cluster",
#     sorted(df["dict_cluster"].unique())
# )

# subset = df[df["dict_cluster"] == selected_cluster]

# st.write(f"**Papers in {selected_cluster}: {len(subset)}**")

# st.dataframe(
#     subset[
#         ["Title", "Journal", "dict_cluster_score", "matched_keywords"]
#     ],
#     use_container_width=True
# )

# # --------------------------------------------------
# # Confidence filtering
# # --------------------------------------------------
# st.header("🎯 Confidence Filtering")

# min_score = st.slider(
#     "Minimum keyword matches",
#     min_value=1,
#     max_value=5,
#     value=1
# )

# filtered = df[df["dict_cluster_score"] >= min_score]

# st.write(f"Papers with score ≥ {min_score}: {len(filtered)}")

# st.dataframe(
#     filtered[
#         ["Title", "dict_cluster", "dict_cluster_score"]
#     ],
#     use_container_width=True
# )

# # --------------------------------------------------
# # Export results
# # --------------------------------------------------
# st.header("📤 Export Results")

# csv = df.to_csv(index=False).encode("utf-8")

# st.download_button(
#     "Download dictionary-clustered CSV",
#     csv,
#     "dictionary_clustered_journals.csv",
#     "text/csv"
# )




# import streamlit as st
# import pandas as pd
# import json
# import re
# import matplotlib.pyplot as plt

# # --------------------------------------------------
# # Streamlit setup
# # --------------------------------------------------
# st.set_page_config(layout="wide")
# st.title("🧭 Dictionary-Based Journal Clustering")

# # --------------------------------------------------
# # Load cluster dictionary
# # --------------------------------------------------
# @st.cache_data
# def load_clusters(path="data/cluster.json"):
#     with open(path, "r") as f:
#         return json.load(f)

# clusters = load_clusters()

# st.sidebar.header("📘 Cluster Dictionary")
# st.sidebar.json(clusters)

# # --------------------------------------------------
# # Load dataset
# # --------------------------------------------------
# @st.cache_data
# def load_data(file):
#     return pd.read_csv(file)

# uploaded_file = st.file_uploader("Upload journal CSV", type=["csv"])
# if not uploaded_file:
#     st.stop()

# df = load_data(uploaded_file)

# # --------------------------------------------------
# # Basic cleaning (safe)
# # --------------------------------------------------
# df["Title"] = df["Title"].fillna("")
# df["Abstract"] = df.get("Abstract", "").fillna("")
# df["Journal"] = df.get("Journal", "Unknown").fillna("Unknown")

# # --------------------------------------------------
# # Text selection
# # --------------------------------------------------
# text_source = st.sidebar.selectbox(
#     "Text used for matching",
#     ["Title only", "Title + Abstract"]
# )

# if text_source == "Title + Abstract":
#     df["text"] = (df["Title"] + " " + df["Abstract"]).str.lower()
# else:
#     df["text"] = df["Title"].str.lower()

# # --------------------------------------------------
# # Keyword matching logic
# # --------------------------------------------------
# def score_text_against_clusters(text, cluster_dict):
#     scores = {}
#     matches = {}

#     for cluster, keywords in cluster_dict.items():
#         found = []
#         score = 0

#         for kw in keywords:
#             pattern = r"\b" + re.escape(kw.lower()) + r"\b"
#             if re.search(pattern, text):
#                 found.append(kw)
#                 score += 1

#         scores[cluster] = score
#         matches[cluster] = found

#     return scores, matches

# # --------------------------------------------------
# # Apply clustering
# # --------------------------------------------------
# cluster_labels = []
# cluster_scores = []
# cluster_matches = []

# for text in df["text"]:
#     scores, matches = score_text_against_clusters(text, clusters)
#     best_cluster = max(scores, key=scores.get)

#     if scores[best_cluster] == 0:
#         cluster_labels.append("Unclassified")
#         cluster_scores.append(0)
#         cluster_matches.append([])
#     else:
#         cluster_labels.append(best_cluster)
#         cluster_scores.append(scores[best_cluster])
#         cluster_matches.append(matches[best_cluster])

# df["dict_cluster"] = cluster_labels
# df["dict_cluster_score"] = cluster_scores
# df["matched_keywords"] = cluster_matches

# # --------------------------------------------------
# # Results overview
# # --------------------------------------------------
# st.header("📊 Cluster Distribution")

# dist = df["dict_cluster"].value_counts()
# st.bar_chart(dist)

# # --------------------------------------------------
# # Inspect cluster
# # --------------------------------------------------
# st.header("🔍 Inspect Cluster")

# selected_cluster = st.selectbox(
#     "Select cluster",
#     sorted(df["dict_cluster"].unique())
# )

# subset = df[df["dict_cluster"] == selected_cluster]

# st.write(f"**Papers in {selected_cluster}: {len(subset)}**")

# st.dataframe(
#     subset[
#         ["Title", "Journal", "dict_cluster_score", "matched_keywords"]
#     ], # .head(25)
#     use_container_width=True
# )

# # --------------------------------------------------
# # Confidence filtering
# # --------------------------------------------------
# st.header("🎯 Confidence Filtering")

# min_score = st.slider("Minimum keyword matches", 1, 5, 1)

# filtered = df[df["dict_cluster_score"] >= min_score]

# st.write(f"Papers with score ≥ {min_score}: {len(filtered)}")

# st.dataframe(
#     filtered[
#         ["Title", "dict_cluster", "dict_cluster_score"]
#     ],
#     use_container_width=True
# )

# # --------------------------------------------------
# # Export
# # --------------------------------------------------
# st.header("📤 Export Results")

# csv = df.to_csv(index=False).encode("utf-8")

# st.download_button(
#     "Download dictionary-clustered CSV",
#     csv,
#     "dictionary_clustered_journals.csv",
#     "text/csv"
# )
