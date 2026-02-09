import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# CONFIG
# --------------------------------------------------
DATA_FOLDER = Path("data/html_google_scholar")


# --------------------------------------------------
# Function to extract information from HTML
# --------------------------------------------------
def extract_scholar_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    results = []

    for result in soup.find_all("div", class_="gs_ri"):
        title_tag = result.find("h3", class_="gs_rt")

        title = title_tag.text if title_tag else "N/A"
        link = title_tag.a["href"] if title_tag and title_tag.a else "N/A"

        publication_info = result.find("div", class_="gs_a")
        publication_info = publication_info.text if publication_info else "N/A"

        snippet = result.find("div", class_="gs_rs")
        snippet = snippet.text if snippet else "N/A"

        results.append(
            {
                "Title": title,
                "Link": link,
                "Publication Info": publication_info,
                "Snippet": snippet,
            }
        )

    return results


# --------------------------------------------------
# Discover HTML files
# --------------------------------------------------
def discover_html_files(folder_path):
    if not folder_path.exists():
        return []

    return sorted(folder_path.glob("*.html"))


# --------------------------------------------------
# Main App
# --------------------------------------------------
def main():
    st.set_page_config(page_title="Scholar HTML Extractor", layout="wide")
    st.title("📚 Google Scholar HTML Extractor")

    # --------------------------
    # Discover files
    # --------------------------
    html_files = discover_html_files(DATA_FOLDER)

    if not html_files:
        st.warning(f"No HTML files found in `{DATA_FOLDER}`")
        return

    # --------------------------
    # File Selector
    # --------------------------
    selected_file = st.selectbox(
        "📂 Select HTML File",
        html_files,
        format_func=lambda x: x.name
    )

    # --------------------------
    # Load Selected File
    # --------------------------
    if selected_file:
        try:
            with open(selected_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            extracted_data = extract_scholar_data(html_content)

            if not extracted_data:
                st.warning("No data extracted. HTML structure may differ.")
                return

            df = pd.DataFrame(extracted_data)

            # --------------------------
            # Show Table
            # --------------------------
            st.header("📊 Extracted Results")
            st.dataframe(df, use_container_width=True)

            # --------------------------
            # Download CSV
            # --------------------------
            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"{selected_file.stem}_results.csv",
                mime="text/csv"
            )

            # --------------------------
            # Detailed View
            # --------------------------
            with st.expander("🔍 Detailed Results"):
                for i, item in enumerate(extracted_data, 1):
                    st.subheader(f"{i}. {item['Title']}")
                    st.markdown(f"**Publication Info:** {item['Publication Info']}")
                    st.markdown(f"**Snippet:** {item['Snippet']}")
                    st.markdown(f"[📄 Open Paper]({item['Link']})")
                    st.markdown("---")

        except Exception as e:
            st.error(f"Error reading file: {e}")


# --------------------------------------------------
# Run App
# --------------------------------------------------
if __name__ == "__main__":
    main()


# import streamlit as st
# from bs4 import BeautifulSoup
# import pandas as pd

# # --------------------------------------------------
# # Function to extract information from the HTML file
# # --------------------------------------------------
# def extract_scholar_data(html_content):
#     soup = BeautifulSoup(html_content, 'html.parser')
#     results = []

#     for result in soup.find_all('div', class_='gs_ri'):
#         title_tag = result.find('h3', class_='gs_rt')
#         title = title_tag.text if title_tag else 'N/A'
#         link = title_tag.a['href'] if title_tag and title_tag.a else 'N/A'

#         publication_info = result.find('div', class_='gs_a')
#         publication_info = publication_info.text if publication_info else 'N/A'

#         snippet = result.find('div', class_='gs_rs')
#         snippet = snippet.text if snippet else 'N/A'

#         results.append({
#             'Title': title,
#             'Link': link,
#             'Publication Info': publication_info,
#             'Snippet': snippet
#         })

#     return results


# # -----------------
# # Main Streamlit App
# # -----------------
# def main():
#     st.title('Google Scholar Data Extractor')

#     try:
#         with open('data/html_google_scholar/1.html', 'r', encoding='utf-8') as f:
#             html_content = f.read()

#         extracted_data = extract_scholar_data(html_content)

#         if not extracted_data:
#             st.warning("No data could be extracted. Please check the HTML structure.")
#             return

#         # -----------------
#         # Create DataFrame
#         # -----------------
#         df = pd.DataFrame(extracted_data)

#         st.header("📊 Extracted Results Table")
#         st.dataframe(df, use_container_width=True)

#         # -----------------
#         # Download as CSV
#         # -----------------
#         csv = df.to_csv(index=False).encode("utf-8")
#         st.download_button(
#             label="⬇️ Download as CSV",
#             data=csv,
#             file_name="google_scholar_results.csv",
#             mime="text/csv"
#         )

#         # -----------------
#         # Optional: Detailed View
#         # -----------------
#         with st.expander("🔍 View Individual Results"):
#             for i, item in enumerate(extracted_data, 1):
#                 st.subheader(f"Result {i}: {item['Title']}")
#                 st.markdown(f"**Publication Info:** {item['Publication Info']}")
#                 st.markdown(f"**Snippet:** *{item['Snippet']}*")
#                 st.markdown(f"[Link to paper]({item['Link']})")
#                 st.markdown("---")

#     except FileNotFoundError:
#         st.error("The file data/html_google_scholar/1.html was not found.")
#     except Exception as e:
#         st.error(f"An error occurred: {e}")


# if __name__ == '__main__':
#     main()


# import streamlit as st
# from bs4 import BeautifulSoup
# import pandas as pd

# # Function to extract information from the HTML file
# def extract_scholar_data(html_content):
#     soup = BeautifulSoup(html_content, 'html.parser')
#     results = []
#     for result in soup.find_all('div', class_='gs_ri'):
#         title = result.find('h3', class_='gs_rt').text
#         link = result.find('h3', class_='gs_rt').a['href'] if result.find('h3', class_='gs_rt').a else 'N/A'
        
#         # Extract authors and publication year
#         publication_info = result.find('div', class_='gs_a').text
        
#         # Extract snippet
#         snippet = result.find('div', class_='gs_rs').text
        
#         results.append({
#             'Title': title,
#             'Link': link,
#             'Publication Info': publication_info,
#             'Snippet': snippet
#         })
#     return results

# # Main app
# def main():
#     st.title('Google Scholar Data Extractor')

#     # Load the HTML file
#     try:
#         with open('data/html_google_scholar/1.html', 'r', encoding='utf-8') as f:
#             html_content = f.read()
        
#         st.header('Extracted Search Results')
#         extracted_data = extract_scholar_data(html_content)
        
#         if extracted_data:
#             # Display data in a more structured way
#             for i, item in enumerate(extracted_data, 1):
#                 st.subheader(f"Result {i}: {item['Title']}")
#                 st.markdown(f"**Publication Info:** {item['Publication Info']}")
#                 st.markdown(f"**Snippet:** *{item['Snippet']}*")
#                 st.markdown(f"[Link to paper]({item['Link']})")
#                 st.markdown("---")
#         else:
#             st.warning("No data could be extracted. Please check the HTML structure.")

#     except FileNotFoundError:
#         st.error("The file data/html_google_scholar/1.html was not found.")
#     except Exception as e:
#         st.error(f"An error occurred: {e}")

# if __name__ == '__main__':
#     main()