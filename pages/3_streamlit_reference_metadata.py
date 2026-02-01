import streamlit as st
import pandas as pd
import re
import requests
from urllib.parse import urlparse

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="📑 Reference Metadata Builder",
    layout="wide"
)

st.title("📑 Unique Reference Metadata Builder")
st.caption("Deduplicate URLs, extract arXiv IDs, generate canonical DOIs, and build PDF links")

# =========================================================
# INPUT
# =========================================================
raw_urls = st.text_area(
    "Paste reference URLs (one per line)",
    height=350,
    placeholder="https://arxiv.org/abs/1911.02116\nhttps://doi.org/10.1145/3571730"
)

# =========================================================
# HELPERS
# =========================================================
def normalize_url(url: str) -> str:
    return url.strip().rstrip("/")


def extract_arxiv_id(url: str):
    """
    Supports:
      - 1911.02116
      - 1911.02116v2
      - hep-th/9901001
    """
    patterns = [
        r"arxiv\.org/(abs|pdf)/([0-9]{4}\.[0-9]{4,5}(v\d+)?)",
        r"arxiv\.org/(abs|pdf)/([a-z\-]+\/[0-9]{7}(v\d+)?)"
    ]

    for p in patterns:
        m = re.search(p, url, re.IGNORECASE)
        if m:
            return m.group(2)

    return None


def arxiv_pdf_url(arxiv_id: str):
    if not arxiv_id:
        return None
    return f"https://arxiv.org/pdf/{arxiv_id}.pdf"


def arxiv_metadata(arxiv_id: str):
    """
    Used ONLY for title extraction.
    DOI is normalized separately.
    """
    api = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    try:
        r = requests.get(api, timeout=10)
        if r.status_code != 200:
            return None
    except Exception:
        return None

    title_match = re.search(r"<title>(.*?)</title>", r.text, re.DOTALL)
    if not title_match:
        return None

    return title_match.group(1).replace("\n", " ").strip()


def doi_metadata(doi_url: str):
    headers = {"Accept": "application/vnd.citationstyles.csl+json"}
    try:
        r = requests.get(doi_url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None, None
    except Exception:
        return None, None

    data = r.json()
    title = (
        data.get("title")[0]
        if isinstance(data.get("title"), list)
        else data.get("title")
    )
    return title, data.get("DOI")


# =========================================================
# PROCESS
# =========================================================
if st.button("🔍 Build Metadata Table") and raw_urls.strip():

    urls = [normalize_url(u) for u in raw_urls.splitlines() if u.strip()]
    unique_urls = sorted(set(urls))

    rows = []

    for url in unique_urls:
        parsed = urlparse(url)

        row = {
            "raw_url": url,
            "canonical_url": url,
            "source_type": None,
            "arxiv_id": None,
            "pdf_url": None,
            "title": None,
            "doi": None
        }

        dois = []

        # ---------------- arXiv ----------------
        if "arxiv.org" in parsed.netloc:
            arxiv_id = extract_arxiv_id(url)

            row["source_type"] = "arxiv"
            row["arxiv_id"] = arxiv_id
            row["pdf_url"] = arxiv_pdf_url(arxiv_id)

            if arxiv_id:
                # Canonical arXiv DOI (DataCite)
                arxiv_doi = f"10.48550/arXiv.{arxiv_id}"
                dois.append(arxiv_doi)

                # Title from arXiv
                row["title"] = arxiv_metadata(arxiv_id)

        # ---------------- DOI ----------------
        elif "doi.org" in parsed.netloc:
            row["source_type"] = "doi"
            title, doi = doi_metadata(url)
            row["title"] = title
            if doi:
                dois.append(doi)

        # ---------------- Other ----------------
        else:
            row["source_type"] = "other"

        # ---------- Final DOI field ----------
        row["doi"] = ",".join(sorted(set(dois))) if dois else None

        rows.append(row)

    df = pd.DataFrame(rows)

    # =====================================================
    # DISPLAY
    # =====================================================
    st.subheader("📊 Reference Metadata Table")
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "⬇️ Download CSV",
        df.to_csv(index=False),
        "reference_metadata.csv",
        "text/csv"
    )

    st.subheader("🧾 Raw JSON Preview")
    st.json(rows)


# import streamlit as st
# import pandas as pd
# import re
# import requests
# from urllib.parse import urlparse

# # =========================================================
# # PAGE CONFIG
# # =========================================================
# st.set_page_config(
#     page_title="📑 Reference Metadata Builder",
#     layout="wide"
# )

# st.title("📑 Unique Reference Metadata Builder")
# st.caption("Deduplicate URLs, extract arXiv IDs, fetch titles, DOIs, and PDF links")

# # =========================================================
# # INPUT
# # =========================================================
# raw_urls = st.text_area(
#     "Paste reference URLs (one per line)",
#     height=350,
#     placeholder="https://arxiv.org/abs/1911.02116\nhttps://doi.org/10.1145/3571730"
# )

# # =========================================================
# # HELPERS
# # =========================================================
# def normalize_url(url: str) -> str:
#     return url.strip().rstrip("/")


# def extract_arxiv_id(url: str):
#     """
#     Supports:
#       - 1911.02116
#       - 1911.02116v2
#       - hep-th/9901001
#     """
#     patterns = [
#         r"arxiv\.org/(abs|pdf)/([0-9]{4}\.[0-9]{4,5}(v\d+)?)",
#         r"arxiv\.org/(abs|pdf)/([a-z\-]+\/[0-9]{7}(v\d+)?)"
#     ]

#     for p in patterns:
#         m = re.search(p, url, re.IGNORECASE)
#         if m:
#             return m.group(2)

#     return None


# def arxiv_pdf_url(arxiv_id: str):
#     if not arxiv_id:
#         return None
#     return f"https://arxiv.org/pdf/{arxiv_id}.pdf"


# def arxiv_metadata(arxiv_id: str):
#     api = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
#     try:
#         r = requests.get(api, timeout=10)
#         if r.status_code != 200:
#             return None, None
#     except Exception:
#         return None, None

#     title_match = re.search(r"<title>(.*?)</title>", r.text, re.DOTALL)
#     doi_match = re.search(r"<arxiv:doi.*?>(.*?)</arxiv:doi>", r.text)

#     title = (
#         title_match.group(1)
#         .replace("\n", " ")
#         .strip()
#         if title_match else None
#     )

#     return title, doi_match.group(1) if doi_match else None


# def doi_metadata(doi_url: str):
#     headers = {
#         "Accept": "application/vnd.citationstyles.csl+json"
#     }
#     try:
#         r = requests.get(doi_url, headers=headers, timeout=10)
#         if r.status_code != 200:
#             return None, None
#     except Exception:
#         return None, None

#     data = r.json()
#     title = (
#         data.get("title")[0]
#         if isinstance(data.get("title"), list)
#         else data.get("title")
#     )
#     return title, data.get("DOI")


# # =========================================================
# # PROCESS
# # =========================================================
# if st.button("🔍 Build Metadata Table") and raw_urls.strip():

#     urls = [normalize_url(u) for u in raw_urls.splitlines() if u.strip()]
#     unique_urls = sorted(set(urls))

#     rows = []

#     for url in unique_urls:
#         parsed = urlparse(url)

#         row = {
#             "raw_url": url,
#             "canonical_url": url,
#             "source_type": None,
#             "arxiv_id": None,
#             "pdf_url": None,
#             "title": None,
#             "doi": None
#         }

#         # ---------------- arXiv ----------------
#         if "arxiv.org" in parsed.netloc:
#             arxiv_id = extract_arxiv_id(url)

#             row["source_type"] = "arxiv"
#             row["arxiv_id"] = arxiv_id
#             row["pdf_url"] = arxiv_pdf_url(arxiv_id)

#             if arxiv_id:
#                 title, doi = arxiv_metadata(arxiv_id)
#                 row["title"] = title
#                 row["doi"] = doi

#         # ---------------- DOI ----------------
#         elif "doi.org" in parsed.netloc:
#             row["source_type"] = "doi"
#             title, doi = doi_metadata(url)
#             row["title"] = title
#             row["doi"] = doi

#         # ---------------- Other ----------------
#         else:
#             row["source_type"] = "other"

#         rows.append(row)

#     df = pd.DataFrame(rows)

#     # =====================================================
#     # DISPLAY
#     # =====================================================
#     st.subheader("📊 Reference Metadata Table")
#     st.dataframe(df, use_container_width=True)

#     st.download_button(
#         "⬇️ Download CSV",
#         df.to_csv(index=False),
#         "reference_metadata.csv",
#         "text/csv"
#     )

#     st.subheader("🧾 Raw JSON Preview")
#     st.json(rows)


# import streamlit as st
# import pandas as pd
# import re
# import requests
# from urllib.parse import urlparse

# # =========================================================
# # PAGE CONFIG
# # =========================================================
# st.set_page_config(page_title="📑 Reference Metadata Builder", layout="wide")
# st.title("📑 Unique Reference Metadata Builder")
# st.caption("Deduplicate URLs, fetch titles, DOIs, and generate PDF links")

# # =========================================================
# # INPUT
# # =========================================================
# raw_urls = st.text_area(
#     "Paste reference URLs (one per line)",
#     height=350
# )

# # =========================================================
# # HELPERS
# # =========================================================
# def normalize_url(url):
#     return url.strip().rstrip("/")


# def extract_arxiv_id(url):
#     m = re.search(r"arxiv\\.org/(abs|pdf)/([0-9\\.]+)", url)
#     return m.group(2) if m else None


# def arxiv_metadata(arxiv_id):
#     api = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
#     r = requests.get(api, timeout=10)
#     if r.status_code != 200:
#         return None, None

#     title = re.search(r"<title>(.*?)</title>", r.text, re.DOTALL)
#     doi = re.search(r"<arxiv:doi.*?>(.*?)</arxiv:doi>", r.text)

#     clean_title = (
#         title.group(1).strip().replace("\n", " ")
#         if title else None
#     )

#     return clean_title, doi.group(1) if doi else None


# def doi_metadata(doi_url):
#     headers = {"Accept": "application/vnd.citationstyles.csl+json"}
#     r = requests.get(doi_url, headers=headers, timeout=10)
#     if r.status_code != 200:
#         return None, None

#     data = r.json()
#     return data.get("title"), data.get("DOI")


# # =========================================================
# # PROCESS
# # =========================================================
# if st.button("🔍 Build Metadata Table") and raw_urls.strip():

#     urls = [normalize_url(u) for u in raw_urls.splitlines() if u.strip()]
#     unique_urls = sorted(set(urls))

#     rows = []

#     for url in unique_urls:
#         parsed = urlparse(url)

#         row = {
#             "raw_url": url,
#             "canonical_url": url,
#             "source_type": None,
#             "arxiv_id": None,
#             "pdf_url": None,
#             "title": None,
#             "doi": None
#         }

#         # ---------- arXiv ----------
#         if "arxiv.org" in parsed.netloc:
#             arxiv_id = extract_arxiv_id(url)
#             row["source_type"] = "arxiv"
#             row["arxiv_id"] = arxiv_id
#             row["pdf_url"] = f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else None

#             if arxiv_id:
#                 title, doi = arxiv_metadata(arxiv_id)
#                 row["title"] = title
#                 row["doi"] = doi

#         # ---------- DOI ----------
#         elif "doi.org" in parsed.netloc:
#             row["source_type"] = "doi"
#             title, doi = doi_metadata(url)
#             row["title"] = title
#             row["doi"] = doi

#         # ---------- Other ----------
#         else:
#             row["source_type"] = "other"

#         rows.append(row)

#     df = pd.DataFrame(rows)

#     # =====================================================
#     # DISPLAY
#     # =====================================================
#     st.subheader("📊 Reference Metadata Table")
#     st.dataframe(df, use_container_width=True)

#     st.download_button(
#         "⬇️ Download CSV",
#         df.to_csv(index=False),
#         "reference_metadata.csv",
#         "text/csv"
#     )

#     st.subheader("🧾 Raw JSON Preview")
#     st.json(rows)
