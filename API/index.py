from flask import Flask, request, jsonify, Response
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

app = Flask(__name__)

# Configure the path for ChromeDriver
CHROMEDRIVER_PATH = "chromedriver"  # Update with your path if necessary

def save_as_mhtml_in_memory(url):
    """Downloads the given URL as an MHTML file and returns its content as a string."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--save-page-as-mhtml')

    # Configure WebDriver
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(3)  # Wait for the page to load (adjust as needed)

        # Get MHTML content via DevTools Protocol
        mhtml_data = driver.execute_cdp_cmd("Page.captureSnapshot", {"format": "mhtml"})
        return mhtml_data.get("data", "")
    finally:
        driver.quit()

@app.route('/api/download_mhtml', methods=['POST'])
def download_mhtml():
    """Endpoint to download a page as a single MHTML document."""
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is required."}), 400

    try:
        mhtml_content = save_as_mhtml_in_memory(url)
        response = Response(mhtml_content, mimetype="multipart/related")
        response.headers["Content-Disposition"] = "attachment; filename=page.mhtml"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Entry point for Vercel
def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    app.run(debug=True)
