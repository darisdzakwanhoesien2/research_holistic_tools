import streamlit as st
from utils.data_loader import data_source_selector
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

st.title("🧠 Thematic Clustering")

df = data_source_selector()

n_topics = st.slider("Number of themes", 3, 20, 8)

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=7000,
    min_df=5
)

X = vectorizer.fit_transform(df["Abstract"].fillna(""))

model = KMeans(n_clusters=n_topics, random_state=42)
df["theme"] = model.fit_predict(X)

st.session_state["clustered_df"] = df
st.session_state["vectorizer"] = vectorizer
st.session_state["model"] = model

theme = st.selectbox("Select Theme", sorted(df.theme.unique()))

subset = df[df.theme == theme]

st.dataframe(subset[["Title", "Journal", "Year"]], use_container_width=True)

terms = vectorizer.get_feature_names_out()
centroid = model.cluster_centers_[theme]
keywords = sorted(zip(centroid, terms), reverse=True)[:12]

st.subheader("Top Keywords")
st.write([k for _, k in keywords])
