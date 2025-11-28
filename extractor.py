import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def extract_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return f"Error: {str(e)}"

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove unwanted elements
    for tag in soup(["script", "style", "img", "nav", "footer", "header"]):
        tag.extract()

    text = soup.get_text(separator="\n")
    cleaned_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])

    return cleaned_text


if __name__ == "__main__":
    url = input("Paste URL: ").strip()
    content = extract_content(url)
    print("\n--- Extracted Content ---\n")
    print(content)
