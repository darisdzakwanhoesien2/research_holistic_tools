import streamlit as st

def get_clustered_df():
    if "clustered_df" not in st.session_state:
        st.warning("Please run Thematic Clustering first.")
        st.stop()
    return st.session_state["clustered_df"]
