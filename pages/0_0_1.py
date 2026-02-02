import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd

# Function to extract information from the HTML file
def extract_scholar_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    for result in soup.find_all('div', class_='gs_ri'):
        title = result.find('h3', class_='gs_rt').text
        link = result.find('h3', class_='gs_rt').a['href'] if result.find('h3', class_='gs_rt').a else 'N/A'
        
        # Extract authors and publication year
        publication_info = result.find('div', class_='gs_a').text
        
        # Extract snippet
        snippet = result.find('div', class_='gs_rs').text
        
        results.append({
            'Title': title,
            'Link': link,
            'Publication Info': publication_info,
            'Snippet': snippet
        })
    return results

# Main app
def main():
    st.title('Google Scholar Data Extractor')

    # Load the HTML file
    try:
        with open('data/html_google_scholar/1.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        st.header('Extracted Search Results')
        extracted_data = extract_scholar_data(html_content)
        
        if extracted_data:
            # Display data in a more structured way
            for i, item in enumerate(extracted_data, 1):
                st.subheader(f"Result {i}: {item['Title']}")
                st.markdown(f"**Publication Info:** {item['Publication Info']}")
                st.markdown(f"**Snippet:** *{item['Snippet']}*")
                st.markdown(f"[Link to paper]({item['Link']})")
                st.markdown("---")
        else:
            st.warning("No data could be extracted. Please check the HTML structure.")

    except FileNotFoundError:
        st.error("The file data/html_google_scholar/1.html was not found.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()