import streamlit as st
from utils.state_helpers import get_clustered_df

st.title("⚖️ Critical Comparison")

# IMPORTANT: use clustered_df to stay consistent
df = get_clustered_df()

tags = (
    df["Tags"]
    .dropna()
    .astype(str)
    .str.split(",")
    .explode()
    .str.strip()
)

tags = sorted(set(tags) - {"", "nan", "None"})

a = st.selectbox("Concept A", tags)
b = st.selectbox("Concept B", tags)

dfa = df[df["Tags"].astype(str).str.contains(a, na=False)]
dfb = df[df["Tags"].astype(str).str.contains(b, na=False)]

st.subheader("Comparison Summary")
st.table({
    "Concept": [a, b],
    "Papers": [len(dfa), len(dfb)],
    "Avg Citations": [
        round(dfa["Cited By"].mean(), 2),
        round(dfb["Cited By"].mean(), 2)
    ]
})

st.subheader("Critical Notes")
st.text_area(
    "Analysis",
    value=f"{a} differs from {b} in terms of methodology, datasets, and evaluation..."
)
