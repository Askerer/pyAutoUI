from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_website(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "無標題"
        text_content = soup.get_text(strip=True)[:500] + "..."
        links = [link.get('href', '') for link in soup.find_all('a')[:5]]
        return title, text_content, links
    except Exception as e:
        return None, str(e), []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        title, text_content, links = scrape_website(url)
        return render_template('index.html', title=title, text_content=text_content, links=links, url=url)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
