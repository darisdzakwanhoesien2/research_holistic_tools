import streamlit as st
from utils.data_loader import data_source_selector

st.title("📊 Data Overview")

df = data_source_selector()

col1, col2, col3 = st.columns(3)
col1.metric("Total Papers", len(df))
col2.metric("Unique Journals", df["Journal"].nunique())
col3.metric("Year Range", f"{df['Year'].min()}–{df['Year'].max()}")

st.subheader("Preview")
st.dataframe(df.head(50), use_container_width=True)

st.subheader("Missing Values")
st.dataframe(df.isna().sum())
