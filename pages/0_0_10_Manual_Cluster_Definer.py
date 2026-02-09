import streamlit as st
import os
import glob
import re
import json
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

DATA_ROOT = "data/ocr_pdf"
APPROVED_FILE = "data/approved_segments.json"

st.title("🧠 Custom Header Segmentation + Clustering (Header-Keyed)")

# ==========================================================
# SAFE PDF FOLDER LISTING
# ==========================================================

pdf_folders = [
    d for d in os.listdir(DATA_ROOT)
    if os.path.isdir(os.path.join(DATA_ROOT, d))
    and not d.startswith(".")
]

if not pdf_folders:
    st.warning("No PDF folders found.")
    st.stop()

selected_pdf = st.sidebar.selectbox("Select PDF Folder", pdf_folders)

# ==========================================================
# LOAD FULL TEXT
# ==========================================================

def read_all_pages(pdf_name):
    folder_path = os.path.join(DATA_ROOT, pdf_name, "pages")

    if not os.path.exists(folder_path):
        return ""

    page_files = sorted(glob.glob(os.path.join(folder_path, "*.md")))

    full_text = ""

    for file in page_files:
        with open(file, "r", encoding="utf-8") as f:
            full_text += f.read() + "\n"

    return full_text


full_text = read_all_pages(selected_pdf)

if not full_text:
    st.warning("No markdown content found.")
    st.stop()

# ==========================================================
# USER HEADER INPUT
# ==========================================================

st.subheader("📌 Provide Custom Header Boundaries")

user_input = st.text_area(
    "Paste Header Lines",
    height=200,
    placeholder="""# Abstract
# 1. Introduction
## 2. Materials and Methods
## 3. Results and Discussion
4. Directions for Future Research
# 5. Conclusions
# References"""
)

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def clean_header(header):
    header = re.sub(r"^#+\s*", "", header)
    header = re.sub(r"^\d+\.\s*", "", header)
    return header.strip()


def split_by_custom_headers(full_text, header_lines):

    cleaned_headers = [clean_header(h) for h in header_lines if h.strip()]

    positions = []

    for header in cleaned_headers:
        match = re.search(re.escape(header), full_text, re.IGNORECASE)
        if match:
            positions.append((match.start(), header))

    positions = sorted(positions, key=lambda x: x[0])

    segments = {}

    if not positions:
        return segments

    # ======================================================
    # 1️⃣ TEXT BEFORE FIRST HEADER
    # ======================================================

    first_start = positions[0][0]

    if first_start > 0:
        pre_text = full_text[:first_start].strip()
        if len(pre_text) > 30:
            segments["Pre-Section"] = pre_text

    # ======================================================
    # 2️⃣ HEADER SEGMENTS
    # ======================================================

    for i in range(len(positions)):

        start = positions[i][0]
        header_label = positions[i][1]

        end = positions[i + 1][0] if i + 1 < len(positions) else len(full_text)

        segment_text = full_text[start:end].strip()

        if len(segment_text) > 30:
            segments[header_label] = segment_text

    return segments


# ==========================================================
# SEGMENTATION
# ==========================================================

if user_input:

    header_lines = user_input.split("\n")

    segments = split_by_custom_headers(full_text, header_lines)

    if not segments:
        st.warning("No matching headers found.")
        st.stop()

    st.subheader("📄 Segments Created")

    df_segments = pd.DataFrame({
        "header": list(segments.keys()),
        "preview": [text[:120] + "..." for text in segments.values()]
    })

    st.dataframe(df_segments)

    # ==========================================================
    # FULL TEXT VIEW
    # ==========================================================

    selected_header = st.selectbox(
        "Select Section to View Full Text",
        list(segments.keys())
    )

    st.text_area(
        "Full Section Text",
        segments[selected_header],
        height=300
    )

    # ==========================================================
    # CLUSTERING
    # ==========================================================

    st.subheader("📊 Run Clustering")

    segment_texts = list(segments.values())
    max_clusters = min(8, len(segment_texts))

    if max_clusters < 2:
        st.info("Not enough segments to cluster.")
    else:

        n_clusters = st.slider(
            "Number of Clusters",
            min_value=2,
            max_value=max_clusters,
            value=2
        )

        if st.button("🚀 Run Clustering"):

            vectorizer = TfidfVectorizer(
                stop_words="english",
                max_features=2000
            )

            X = vectorizer.fit_transform(segment_texts)

            model = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = model.fit_predict(X)

            df_cluster = pd.DataFrame({
                "header": list(segments.keys()),
                "cluster": cluster_labels
            })

            st.subheader("📋 Clustered Sections")
            st.dataframe(df_cluster)

            cluster_counts = df_cluster["cluster"].value_counts().sort_index()

            fig = plt.figure()
            plt.bar(cluster_counts.index.astype(str), cluster_counts.values)
            plt.xlabel("Cluster")
            plt.ylabel("Number of Sections")
            plt.title("Cluster Distribution")

            st.pyplot(fig)

    # ==========================================================
    # APPROVE & STORE
    # ==========================================================

    st.subheader("✅ Approve & Store Segmentation")

    if st.button("Approve Segmentation"):

        os.makedirs("data", exist_ok=True)

        if os.path.exists(APPROVED_FILE):
            with open(APPROVED_FILE, "r", encoding="utf-8") as f:
                approved_data = json.load(f)
        else:
            approved_data = {}

        approved_data[selected_pdf] = segments

        with open(APPROVED_FILE, "w", encoding="utf-8") as f:
            json.dump(approved_data, f, indent=4)

        st.success("Segmentation stored successfully!")


# import streamlit as st
# import os
# import glob
# import re
# import json
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cluster import KMeans

# DATA_ROOT = "data/ocr_pdf"
# APPROVED_FILE = "data/approved_segments.json"

# st.title("🧠 Custom Header Segmentation + Clustering (Full Coverage)")

# # ==========================================================
# # SAFE FOLDER LISTING
# # ==========================================================

# pdf_folders = [
#     d for d in os.listdir(DATA_ROOT)
#     if os.path.isdir(os.path.join(DATA_ROOT, d))
#     and not d.startswith(".")
# ]

# if not pdf_folders:
#     st.warning("No PDF folders found.")
#     st.stop()

# selected_pdf = st.sidebar.selectbox("Select PDF Folder", pdf_folders)

# # ==========================================================
# # LOAD FULL TEXT
# # ==========================================================

# def read_all_pages(pdf_name):
#     folder_path = os.path.join(DATA_ROOT, pdf_name, "pages")

#     page_files = sorted(
#         glob.glob(os.path.join(folder_path, "*.md"))
#     )

#     full_text = ""

#     for file in page_files:
#         with open(file, "r", encoding="utf-8") as f:
#             full_text += f.read() + "\n"

#     return full_text


# full_text = read_all_pages(selected_pdf)

# if not full_text:
#     st.warning("No markdown pages found.")
#     st.stop()

# # ==========================================================
# # USER INPUT HEADERS
# # ==========================================================

# st.subheader("📌 Provide Custom Header Boundaries")

# user_input = st.text_area(
#     "Paste Header Lines",
#     height=180,
#     placeholder="""# Abstract
# # 1. Introduction
# ## 2. Materials and Methods
# ## 3. Results and Discussion
# 4. Directions for Future Research
# # 5. Conclusions
# # References"""
# )

# # ==========================================================
# # HELPER FUNCTIONS
# # ==========================================================

# def clean_header(header):
#     header = re.sub(r"^#+\s*", "", header)
#     header = re.sub(r"^\d+\.\s*", "", header)
#     return header.strip()


# def split_by_custom_headers(full_text, header_lines):

#     cleaned_headers = [clean_header(h) for h in header_lines if h.strip()]

#     positions = []

#     for header in cleaned_headers:
#         match = re.search(re.escape(header), full_text, re.IGNORECASE)
#         if match:
#             positions.append((match.start(), header))

#     positions = sorted(positions, key=lambda x: x[0])

#     segments = []

#     if not positions:
#         return segments

#     # ======================================================
#     # 1️⃣ TEXT BEFORE FIRST HEADER
#     # ======================================================

#     first_start = positions[0][0]

#     if first_start > 0:
#         pre_text = full_text[:first_start].strip()
#         if len(pre_text) > 30:
#             segments.append(pre_text)

#     # ======================================================
#     # 2️⃣ BETWEEN HEADERS
#     # ======================================================

#     for i in range(len(positions)):

#         start = positions[i][0]
#         end = positions[i + 1][0] if i + 1 < len(positions) else len(full_text)

#         segment_text = full_text[start:end].strip()

#         if len(segment_text) > 30:
#             segments.append(segment_text)

#     # ======================================================
#     # 3️⃣ TEXT AFTER LAST HEADER (SAFETY CHECK)
#     # ======================================================

#     last_header_end = positions[-1][0]
#     tail_text = full_text[last_header_end:].strip()

#     if len(tail_text) > 30 and tail_text not in segments:
#         segments.append(tail_text)

#     return segments


# # ==========================================================
# # SEGMENTATION
# # ==========================================================

# if user_input:

#     header_lines = user_input.split("\n")

#     segments = split_by_custom_headers(full_text, header_lines)

#     if not segments:
#         st.warning("No matching headers found in paper.")
#         st.stop()

#     st.subheader("📄 Segments Created (Full Coverage)")

#     df_segments = pd.DataFrame({
#         "segment_id": range(len(segments)),
#         "preview": [s[:120] + "..." for s in segments]
#     })

#     st.dataframe(df_segments)

#     # ==========================================================
#     # FULL TEXT VIEW
#     # ==========================================================

#     selected_segment = st.selectbox(
#         "Select Segment to View Full Text",
#         df_segments["segment_id"]
#     )

#     st.text_area(
#         "Full Segment Text",
#         segments[selected_segment],
#         height=300
#     )

#     # ==========================================================
#     # CLUSTERING
#     # ==========================================================

#     st.subheader("📊 Run Clustering")

#     max_clusters = min(8, len(segments))

#     if max_clusters < 2:
#         st.info("Not enough segments to cluster.")
#     else:

#         n_clusters = st.slider(
#             "Number of Clusters",
#             min_value=2,
#             max_value=max_clusters,
#             value=2
#         )

#         if st.button("🚀 Run Clustering"):

#             vectorizer = TfidfVectorizer(
#                 stop_words="english",
#                 max_features=2000
#             )

#             X = vectorizer.fit_transform(segments)

#             model = KMeans(n_clusters=n_clusters, random_state=42)
#             cluster_labels = model.fit_predict(X)

#             df_segments["cluster"] = cluster_labels

#             st.subheader("📋 Clustered Segments")
#             st.dataframe(df_segments)

#             cluster_counts = df_segments["cluster"].value_counts().sort_index()

#             fig = plt.figure()
#             plt.bar(cluster_counts.index.astype(str), cluster_counts.values)
#             plt.xlabel("Cluster")
#             plt.ylabel("Number of Segments")
#             plt.title("Segment Cluster Distribution")

#             st.pyplot(fig)

#     # ==========================================================
#     # APPROVE & STORE
#     # ==========================================================

#     st.subheader("✅ Approve & Store Segments")

#     if st.button("Approve Segmentation"):

#         os.makedirs("data", exist_ok=True)

#         if os.path.exists(APPROVED_FILE):
#             with open(APPROVED_FILE, "r", encoding="utf-8") as f:
#                 approved_data = json.load(f)
#         else:
#             approved_data = {}

#         approved_data[selected_pdf] = segments

#         with open(APPROVED_FILE, "w", encoding="utf-8") as f:
#             json.dump(approved_data, f, indent=4)

#         st.success("Full segmentation stored successfully!")


# import streamlit as st
# import os
# import glob
# import re
# import json
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cluster import KMeans

# DATA_ROOT = "data/ocr_pdf"
# APPROVED_FILE = "data/approved_segments.json"

# st.title("🧠 Custom Header Segmentation + Clustering")

# # ==========================================================
# # SAFE FOLDER LISTING (NO .DS_STORE ERROR)
# # ==========================================================

# pdf_folders = [
#     d for d in os.listdir(DATA_ROOT)
#     if os.path.isdir(os.path.join(DATA_ROOT, d))
#     and not d.startswith(".")
# ]

# if not pdf_folders:
#     st.warning("No PDF folders found.")
#     st.stop()

# selected_pdf = st.sidebar.selectbox("Select PDF Folder", pdf_folders)

# # ==========================================================
# # LOAD FULL TEXT
# # ==========================================================

# def read_all_pages(pdf_name):
#     folder_path = os.path.join(DATA_ROOT, pdf_name, "pages")

#     if not os.path.exists(folder_path):
#         return ""

#     page_files = sorted(
#         glob.glob(os.path.join(folder_path, "*.md"))
#     )

#     full_text = ""

#     for file in page_files:
#         with open(file, "r", encoding="utf-8") as f:
#             full_text += f.read() + "\n"

#     return full_text


# full_text = read_all_pages(selected_pdf)

# if not full_text:
#     st.warning("No markdown pages found.")
#     st.stop()

# # ==========================================================
# # USER INPUT HEADERS
# # ==========================================================

# st.subheader("📌 Provide Custom Header Boundaries")

# user_input = st.text_area(
#     "Paste Header Lines",
#     height=150,
#     placeholder="## 3. Results and Discussion\n4. Directions for Future Research"
# )

# # ==========================================================
# # HELPER FUNCTIONS
# # ==========================================================

# def clean_header(header):
#     header = re.sub(r"^#+\s*", "", header)
#     header = re.sub(r"^\d+\.\s*", "", header)
#     return header.strip()


# def split_by_custom_headers(full_text, header_lines):

#     cleaned_headers = [clean_header(h) for h in header_lines if h.strip()]

#     positions = []

#     for header in cleaned_headers:
#         match = re.search(re.escape(header), full_text, re.IGNORECASE)
#         if match:
#             positions.append((match.start(), header))

#     positions = sorted(positions, key=lambda x: x[0])

#     segments = []

#     if not positions:
#         return segments

#     # ------------------------------------------
#     # 1️⃣ TEXT BEFORE FIRST HEADER
#     # ------------------------------------------

#     first_start = positions[0][0]

#     if first_start > 0:
#         pre_text = full_text[:first_start].strip()
#         if len(pre_text) > 50:
#             segments.append(pre_text)

#     # ------------------------------------------
#     # 2️⃣ HEADER SEGMENTS
#     # ------------------------------------------

#     for i in range(len(positions)):
#         start = positions[i][0]
#         end = positions[i + 1][0] if i + 1 < len(positions) else len(full_text)

#         segment_text = full_text[start:end].strip()
#         segments.append(segment_text)

#     return segments


# # ==========================================================
# # SEGMENTATION
# # ==========================================================

# if user_input:

#     header_lines = user_input.split("\n")

#     segments = split_by_custom_headers(full_text, header_lines)

#     if not segments:
#         st.warning("No matching headers found in paper.")
#         st.stop()

#     st.subheader("📄 Segments Created")

#     df_segments = pd.DataFrame({
#         "segment_id": range(len(segments)),
#         "preview": [s[:120] + "..." for s in segments]
#     })

#     st.dataframe(df_segments)

#     # ==========================================================
#     # FULL TEXT VIEW
#     # ==========================================================

#     selected_segment = st.selectbox(
#         "Select Segment to View Full Text",
#         df_segments["segment_id"]
#     )

#     st.text_area(
#         "Full Segment Text",
#         segments[selected_segment],
#         height=300
#     )

#     # ==========================================================
#     # CLUSTERING (SAFE SLIDER)
#     # ==========================================================

#     st.subheader("📊 Run Clustering")

#     max_clusters = min(8, len(segments))

#     if max_clusters < 2:
#         st.info("Not enough segments to cluster.")
#     else:

#         n_clusters = st.slider(
#             "Number of Clusters",
#             min_value=2,
#             max_value=max_clusters,
#             value=2
#         )

#         if st.button("🚀 Run Clustering"):

#             vectorizer = TfidfVectorizer(
#                 stop_words="english",
#                 max_features=2000
#             )

#             X = vectorizer.fit_transform(segments)

#             model = KMeans(n_clusters=n_clusters, random_state=42)
#             cluster_labels = model.fit_predict(X)

#             df_segments["cluster"] = cluster_labels

#             st.subheader("📋 Clustered Segments")
#             st.dataframe(df_segments)

#             # Distribution plot

#             cluster_counts = df_segments["cluster"].value_counts().sort_index()

#             fig = plt.figure()
#             plt.bar(cluster_counts.index.astype(str), cluster_counts.values)
#             plt.xlabel("Cluster")
#             plt.ylabel("Number of Segments")
#             plt.title("Segment Cluster Distribution")

#             st.pyplot(fig)

#     # ==========================================================
#     # APPROVE & STORE
#     # ==========================================================

#     st.subheader("✅ Approve Segmentation")

#     if st.button("Approve & Store Segments"):

#         os.makedirs("data", exist_ok=True)

#         if os.path.exists(APPROVED_FILE):
#             with open(APPROVED_FILE, "r", encoding="utf-8") as f:
#                 approved_data = json.load(f)
#         else:
#             approved_data = {}

#         approved_data[selected_pdf] = segments

#         with open(APPROVED_FILE, "w", encoding="utf-8") as f:
#             json.dump(approved_data, f, indent=4)

#         st.success("Segments stored successfully!")



# import streamlit as st
# import os
# import glob
# import re
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cluster import KMeans

# DATA_ROOT = "data/ocr_pdf"

# st.title("🧠 Custom Header-Based Segmentation + Clustering")

# # ==========================================================
# # SELECT PDF
# # ==========================================================

# pdf_folders = [
#     d for d in os.listdir(DATA_ROOT)
#     if os.path.isdir(os.path.join(DATA_ROOT, d))
# ]

# selected_pdf = st.sidebar.selectbox("Select PDF Folder", pdf_folders)

# # ==========================================================
# # LOAD FULL TEXT
# # ==========================================================

# def read_all_pages(pdf_name):
#     folder_path = os.path.join(DATA_ROOT, pdf_name, "pages")
#     page_files = sorted(glob.glob(os.path.join(folder_path, "*.md")))

#     full_text = ""
#     for file in page_files:
#         with open(file, "r", encoding="utf-8") as f:
#             full_text += f.read() + "\n"

#     return full_text


# full_text = read_all_pages(selected_pdf)

# # ==========================================================
# # USER INPUT HEADERS
# # ==========================================================

# st.subheader("📌 Provide Header Boundaries")

# user_input = st.text_area(
#     "Paste Header Lines",
#     height=150,
#     placeholder="## 3. Results and Discussion\n4. Directions for Future Research"
# )

# # ==========================================================
# # CLEAN HEADER INPUT
# # ==========================================================

# def clean_header(header):
#     header = re.sub(r"^#+\s*", "", header)
#     header = re.sub(r"^\d+\.\s*", "", header)
#     return header.strip()


# def split_by_custom_headers(full_text, header_lines):

#     cleaned_headers = [clean_header(h) for h in header_lines]

#     # Find positions
#     positions = []

#     for header in cleaned_headers:
#         match = re.search(re.escape(header), full_text, re.IGNORECASE)
#         if match:
#             positions.append((match.start(), header))

#     positions = sorted(positions, key=lambda x: x[0])

#     segments = []

#     for i in range(len(positions)):
#         start = positions[i][0]
#         end = positions[i + 1][0] if i + 1 < len(positions) else len(full_text)

#         segment_text = full_text[start:end].strip()
#         segments.append(segment_text)

#     return segments


# if user_input:

#     header_lines = [line for line in user_input.split("\n") if line.strip()]

#     segments = split_by_custom_headers(full_text, header_lines)

#     if segments:

#         st.subheader("📄 Segments Created")

#         df_segments = pd.DataFrame({
#             "segment_id": range(len(segments)),
#             "text_preview": [s[:120] + "..." for s in segments]
#         })

#         st.dataframe(df_segments)

#         # ======================================================
#         # CLUSTERING
#         # ======================================================

#         n_clusters = st.slider(
#             "Number of Clusters",
#             min_value=2,
#             max_value=min(8, len(segments)),
#             value=min(2, len(segments))
#         )

#         if st.button("🚀 Run Clustering"):

#             vectorizer = TfidfVectorizer(stop_words="english")
#             X = vectorizer.fit_transform(segments)

#             model = KMeans(n_clusters=n_clusters, random_state=42)
#             cluster_labels = model.fit_predict(X)

#             df_segments["cluster"] = cluster_labels

#             st.subheader("📊 Clustered Segments")
#             st.dataframe(df_segments)

#             # --------------------------------------------------
#             # Distribution
#             # --------------------------------------------------

#             cluster_counts = df_segments["cluster"].value_counts().sort_index()

#             fig = plt.figure()
#             plt.bar(cluster_counts.index.astype(str), cluster_counts.values)
#             plt.xlabel("Cluster")
#             plt.ylabel("Number of Segments")
#             plt.title("Segment Cluster Distribution")

#             st.pyplot(fig)

#             # --------------------------------------------------
#             # Inspect Cluster
#             # --------------------------------------------------

#             st.subheader("🔍 Inspect Cluster")

#             selected_cluster = st.selectbox(
#                 "Select Cluster",
#                 sorted(df_segments["cluster"].unique())
#             )

#             cluster_segments = df_segments[df_segments["cluster"] == selected_cluster]

#             for idx, row in cluster_segments.iterrows():
#                 st.markdown("---")
#                 st.markdown(f"**Segment {row.segment_id}**")
#                 st.write(segments[row.segment_id])

#     else:
#         st.warning("No matching headers found in paper.")


# import streamlit as st
# import os
# import glob
# import re
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cluster import KMeans

# DATA_ROOT = "data/ocr_pdf"

# st.title("🧠 Header-Based Clustering Explorer")

# # ==========================================================
# # SELECT PDF
# # ==========================================================

# pdf_folders = [
#     d for d in os.listdir(DATA_ROOT)
#     if os.path.isdir(os.path.join(DATA_ROOT, d))
# ]

# selected_pdf = st.sidebar.selectbox("Select PDF Folder", pdf_folders)

# # ==========================================================
# # LOAD FULL TEXT
# # ==========================================================

# def read_all_pages(pdf_name):
#     folder_path = os.path.join(DATA_ROOT, pdf_name, "pages")
#     page_files = sorted(glob.glob(os.path.join(folder_path, "*.md")))

#     full_text = ""
#     for file in page_files:
#         with open(file, "r", encoding="utf-8") as f:
#             full_text += f.read() + "\n"

#     return full_text


# full_text = read_all_pages(selected_pdf)

# # ==========================================================
# # EXTRACT HEADERS ONLY
# # ==========================================================

# def extract_headers(text):

#     pattern = r"(^\s*#+\s+.*$|^\s*\d+\.\s+.*$)"
#     matches = re.findall(pattern, text, re.MULTILINE)

#     cleaned_headers = []

#     for header in matches:
#         # remove markdown symbols
#         header = re.sub(r"^#+\s*", "", header)

#         # remove numbering like 3.
#         header = re.sub(r"^\d+\.\s*", "", header)

#         cleaned_headers.append(header.strip())

#     return cleaned_headers


# headers = extract_headers(full_text)

# st.write(f"Detected {len(headers)} headers.")

# if headers:

#     df_headers = pd.DataFrame({
#         "header_text": headers
#     })

#     st.subheader("📋 Extracted Headers")
#     st.dataframe(df_headers)

#     # ==========================================================
#     # CLUSTER HEADERS
#     # ==========================================================

#     n_clusters = st.slider("Number of Clusters", 2, 8, 3)

#     if st.button("🚀 Run Header Clustering"):

#         vectorizer = TfidfVectorizer(stop_words="english")
#         X = vectorizer.fit_transform(headers)

#         model = KMeans(n_clusters=n_clusters, random_state=42)
#         cluster_labels = model.fit_predict(X)

#         df_headers["cluster"] = cluster_labels

#         st.subheader("📊 Clustered Headers")
#         st.dataframe(df_headers)

#         # ------------------------------------------------------
#         # Cluster Distribution
#         # ------------------------------------------------------

#         cluster_counts = df_headers["cluster"].value_counts().sort_index()

#         fig = plt.figure()
#         plt.bar(cluster_counts.index.astype(str), cluster_counts.values)
#         plt.xlabel("Cluster")
#         plt.ylabel("Number of Headers")
#         plt.title("Header Cluster Distribution")

#         st.pyplot(fig)

#         # ------------------------------------------------------
#         # Inspect Cluster
#         # ------------------------------------------------------

#         st.subheader("🔍 Inspect Cluster")

#         selected_cluster = st.selectbox(
#             "Select Cluster",
#             sorted(df_headers["cluster"].unique())
#         )

#         cluster_headers = df_headers[df_headers["cluster"] == selected_cluster]

#         for _, row in cluster_headers.iterrows():
#             st.markdown(f"- {row.header_text}")

# else:
#     st.warning("No headers detected.")


# import streamlit as st
# import os
# import glob
# import re
# import pandas as pd
# import matplotlib.pyplot as plt
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cluster import KMeans

# DATA_ROOT = "data/ocr_pdf"

# st.title("🧠 Paper Text Clustering Explorer")

# # ==========================================================
# # SELECT PDF
# # ==========================================================

# pdf_folders = [
#     d for d in os.listdir(DATA_ROOT)
#     if os.path.isdir(os.path.join(DATA_ROOT, d))
# ]

# selected_pdf = st.sidebar.selectbox("Select PDF Folder", pdf_folders)

# # ==========================================================
# # LOAD FULL TEXT
# # ==========================================================

# def read_all_pages(pdf_name):
#     folder_path = os.path.join(DATA_ROOT, pdf_name, "pages")
#     page_files = sorted(glob.glob(os.path.join(folder_path, "*.md")))

#     full_text = ""
#     for file in page_files:
#         with open(file, "r", encoding="utf-8") as f:
#             full_text += f.read() + "\n"

#     return full_text


# full_text = read_all_pages(selected_pdf)

# # ==========================================================
# # SEGMENTATION OPTIONS
# # ==========================================================

# st.subheader("📌 Segmentation Mode")

# segmentation_mode = st.radio(
#     "Choose segmentation method:",
#     ["By Headers", "By Paragraph"]
# )

# def split_by_headers(text):

#     pattern = r"(^\s*#+\s+.*$|^\s*\d+\.\s+.*$)"
#     matches = list(re.finditer(pattern, text, re.MULTILINE))

#     segments = []

#     for i, match in enumerate(matches):
#         start = match.start()
#         end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
#         segment_text = text[start:end].strip()

#         segments.append(segment_text)

#     return segments


# def split_by_paragraph(text):
#     paragraphs = re.split(r"\n\s*\n", text)
#     return [p.strip() for p in paragraphs if len(p.strip()) > 100]


# if segmentation_mode == "By Headers":
#     segments = split_by_headers(full_text)
# else:
#     segments = split_by_paragraph(full_text)

# st.write(f"Detected {len(segments)} segments.")

# # ==========================================================
# # CLUSTERING
# # ==========================================================

# if segments:

#     n_clusters = st.slider("Number of Clusters", 2, 10, 3)

#     if st.button("🚀 Run Clustering"):

#         vectorizer = TfidfVectorizer(
#             stop_words="english",
#             max_features=2000
#         )

#         X = vectorizer.fit_transform(segments)

#         model = KMeans(n_clusters=n_clusters, random_state=42)
#         cluster_labels = model.fit_predict(X)

#         df_cluster = pd.DataFrame({
#             "segment_id": range(len(segments)),
#             "cluster": cluster_labels,
#             "text": segments
#         })

#         st.subheader("📋 Clustered Segments")
#         st.dataframe(df_cluster[["segment_id", "cluster"]])

#         # --------------------------------------------------
#         # CLUSTER DISTRIBUTION
#         # --------------------------------------------------

#         cluster_counts = df_cluster["cluster"].value_counts().sort_index()

#         fig = plt.figure()
#         plt.bar(cluster_counts.index.astype(str), cluster_counts.values)
#         plt.xlabel("Cluster")
#         plt.ylabel("Number of Segments")
#         plt.title("Segment Cluster Distribution")

#         st.pyplot(fig)

#         # --------------------------------------------------
#         # INSPECT CLUSTERS
#         # --------------------------------------------------

#         st.subheader("🔍 Inspect Cluster")

#         selected_cluster = st.selectbox(
#             "Select Cluster to View",
#             sorted(df_cluster["cluster"].unique())
#         )

#         cluster_segments = df_cluster[df_cluster["cluster"] == selected_cluster]

#         for idx, row in cluster_segments.iterrows():
#             st.markdown(f"---")
#             st.markdown(f"**Segment {row.segment_id}**")
#             st.write(row.text)

# else:
#     st.warning("No segments detected.")


# import streamlit as st
# import re
# import pandas as pd
# import json
# import os

# CLUSTER_MAP_FILE = "data/manual_cluster_map.json"

# st.title("🧠 Manual Cluster Definition Tool")

# # ==========================================================
# # LOAD CLUSTER MAP
# # ==========================================================

# if os.path.exists(CLUSTER_MAP_FILE):
#     with open(CLUSTER_MAP_FILE, "r", encoding="utf-8") as f:
#         cluster_map = json.load(f)
# else:
#     cluster_map = {}

# # ==========================================================
# # TEXT INPUT
# # ==========================================================

# st.subheader("📄 Paste Markdown / Text")

# input_text = st.text_area(
#     "Input Text",
#     height=300,
#     placeholder="## 3. Results and Discussion\n4. Directions for Future Research"
# )

# # ==========================================================
# # DETECT HEADERS
# # ==========================================================

# def detect_headers(text):

#     pattern = r"""
#     (
#         ^\s*#+\s+.*$       |
#         ^\s*\d+\.\s+.*$
#     )
#     """

#     matches = re.findall(pattern, text, re.MULTILINE | re.VERBOSE)
#     headers = [h.strip() for h in matches]

#     return headers


# if input_text:

#     headers = detect_headers(input_text)

#     if headers:

#         st.subheader("🔍 Detected Headers")

#         df_headers = pd.DataFrame({
#             "detected_header": headers
#         })

#         st.dataframe(df_headers)

#         # ======================================================
#         # MANUAL CLUSTER ASSIGNMENT
#         # ======================================================

#         st.subheader("🏷 Assign Cluster Labels")

#         updated_mapping = {}

#         for header in headers:
#             cluster_label = st.text_input(
#                 f"Cluster for: {header}",
#                 value=cluster_map.get(header, "")
#             )
#             updated_mapping[header] = cluster_label

#         if st.button("Save Cluster Mapping"):

#             os.makedirs("data", exist_ok=True)

#             with open(CLUSTER_MAP_FILE, "w", encoding="utf-8") as f:
#                 json.dump(updated_mapping, f, indent=4)

#             st.success("Cluster mapping saved!")

#     else:
#         st.warning("No headers detected.")

# # ==========================================================
# # SHOW EXISTING MAPPING
# # ==========================================================

# if cluster_map:

#     st.subheader("📋 Existing Cluster Definitions")

#     df_map = pd.DataFrame(
#         list(cluster_map.items()),
#         columns=["header", "cluster_label"]
#     )

#     st.dataframe(df_map)
