import os
import pandas as pd
import streamlit as st

LITMAP_DIR = "data/litmap_database"

REQUIRED_COLUMNS = [
    "Title", "Authors", "Journal", "Year",
    "Abstract", "Cited By", "Tags"
]

@st.cache_data
def load_csv(path_or_file):
    if isinstance(path_or_file, str):
        df = pd.read_csv(path_or_file)
    else:
        df = pd.read_csv(path_or_file)

    # Normalize column names (safe)
    df.columns = [c.strip() for c in df.columns]

    # Ensure required columns exist
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = None

    return df


def data_source_selector():
    st.sidebar.header("📂 Data Source")

    option = st.sidebar.radio(
        "Choose data source",
        ["Use existing dataset", "Upload CSV"]
    )

    if option == "Use existing dataset":
        files = [
            f for f in os.listdir(LITMAP_DIR)
            if f.endswith(".csv")
        ]

        selected = st.sidebar.selectbox(
            "Select dataset",
            files
        )

        path = os.path.join(LITMAP_DIR, selected)
        df = load_csv(path)

    else:
        uploaded = st.sidebar.file_uploader(
            "Upload CSV",
            type=["csv"]
        )
        if uploaded is None:
            st.warning("Please upload a CSV file.")
            st.stop()
        df = load_csv(uploaded)

    return df
