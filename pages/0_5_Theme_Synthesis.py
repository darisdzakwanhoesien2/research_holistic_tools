import streamlit as st
from utils.state_helpers import get_clustered_df

st.title("📝 Theme Synthesis")

df = get_clustered_df()

theme = st.selectbox(
    "Select Theme",
    sorted(df["theme"].unique())
)

subset = df[df["theme"] == theme]

st.subheader("Top Papers (by citations)")
st.dataframe(
    subset.sort_values("Cited By", ascending=False)
          .head(10)[["Title", "Journal", "Year", "Cited By"]],
    use_container_width=True
)

# ✅ SAFE tag extraction
tags = (
    subset["Tags"]
    .dropna()
    .astype(str)
    .str.split(",")
    .explode()
    .str.strip()
)

tags = tags[~tags.isin(["", "nan", "None"])].value_counts()

st.subheader("Common Tags")
st.write(tags.head(10))

st.subheader("Theme Narrative (Editable)")
st.text_area(
    "Draft Theme Summary",
    value=f"This theme (Theme {theme}) focuses on ...",
    height=220
)


# import streamlit as st

# st.title("📝 Theme Synthesis")

# if "clustered_df" not in st.session_state:
#     st.warning("Run thematic clustering first.")
#     st.stop()

# df = st.session_state["clustered_df"]

# theme = st.selectbox("Select Theme", sorted(df.theme.unique()))
# subset = df[df.theme == theme]

# st.dataframe(
#     subset.sort_values("Cited By", ascending=False)
#           .head(10)[["Title", "Journal", "Year", "Cited By"]],
#     use_container_width=True
# )

# # ✅ Robust tag handling
# tags = (
#     subset["Tags"]
#     .dropna()
#     .astype(str)
#     .str.split(",")
#     .explode()
#     .str.strip()
# )

# tags = tags[~tags.isin(["", "nan", "None"])].value_counts()

# st.subheader("Common Tags")
# st.write(tags.head(10))

# st.text_area(
#     "Draft Theme Summary",
#     value="This theme focuses on...",
#     height=220
# )


# import streamlit as st

# st.title("📝 Theme Synthesis")

# if "clustered_df" not in st.session_state:
#     st.warning("Run thematic clustering first.")
#     st.stop()

# df = st.session_state["clustered_df"]

# theme = st.selectbox("Select Theme", sorted(df.theme.unique()))
# subset = df[df.theme == theme]

# st.dataframe(
#     subset.sort_values("Cited By", ascending=False)
#           .head(10)[["Title", "Journal", "Year", "Cited By"]],
#     use_container_width=True
# )

# tags = (
#     subset["Tags"]
#     .dropna()
#     .str.split(",")
#     .explode()
#     .str.strip()
#     .value_counts()
# )

# st.subheader("Common Tags")
# st.write(tags.head(10))

# st.text_area(
#     "Draft Theme Summary",
#     value="This theme focuses on...",
#     height=220
# )
