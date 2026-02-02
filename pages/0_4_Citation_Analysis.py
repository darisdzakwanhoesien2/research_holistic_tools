import streamlit as st
from utils.data_loader import data_source_selector

st.title("📈 Citation Analysis")

df = data_source_selector()

st.subheader("Most Cited Papers")
st.dataframe(
    df.sort_values("Cited By", ascending=False)
      .head(25)[["Title", "Journal", "Year", "Cited By"]],
    use_container_width=True
)

st.subheader("Citation Distribution")
st.bar_chart(df["Cited By"])
