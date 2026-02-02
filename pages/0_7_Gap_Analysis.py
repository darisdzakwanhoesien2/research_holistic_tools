import streamlit as st
from utils.data_loader import data_source_selector

st.title("🧩 Gap Analysis")

df = data_source_selector()

tag_counts = (
    df["Tags"].dropna()
    .str.split(",")
    .explode()
    .value_counts()
)

st.subheader("Underexplored Topics")
st.dataframe(tag_counts.tail(20))

recent = df[df.Year >= df.Year.max() - 2]
low = recent[recent["Cited By"] <= recent["Cited By"].quantile(0.25)]

st.subheader("Low-Citation Recent Papers")
st.dataframe(
    low[["Title", "Journal", "Year", "Cited By"]],
    use_container_width=True
)
