import streamlit as st
from utils.data_loader import data_source_selector

st.title("🔍 Paper Explorer")

df = data_source_selector()

query = st.text_input("Search title, abstract, authors, tags")

if query:
    df = df[
        df["Title"].str.contains(query, case=False, na=False) |
        df["Abstract"].str.contains(query, case=False, na=False) |
        df["Authors"].str.contains(query, case=False, na=False) |
        df["Tags"].str.contains(query, case=False, na=False)
    ]

year_min, year_max = int(df.Year.min()), int(df.Year.max())
years = st.slider("Year range", year_min, year_max, (year_min, year_max))
df = df[df.Year.between(*years)]

st.dataframe(
    df[["Title", "Authors", "Journal", "Year", "Cited By"]],
    use_container_width=True
)
