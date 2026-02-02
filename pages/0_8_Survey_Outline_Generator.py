import streamlit as st

st.title("📄 Survey Outline Generator")

if "clustered_df" not in st.session_state:
    st.warning("Run clustering first.")
    st.stop()

df = st.session_state["clustered_df"]

outline = []
outline.append("\\section{Introduction}")
outline.append("Motivation and scope.")

outline.append("\\section{Methodology}")
outline.append("Dataset selection and thematic analysis.")

for t in sorted(df.theme.unique()):
    outline.append(f"\\section{{Theme {t}}}")
    for title in (
        df[df.theme == t]
        .sort_values("Cited By", ascending=False)
        .head(5)["Title"]
    ):
        outline.append(f"\\item {title}")

outline.append("\\section{Future Directions}")

latex = "\n".join(outline)

st.text_area("Generated LaTeX", latex, height=420)

st.download_button(
    "Download LaTeX",
    latex,
    file_name="survey_outline.tex"
)
