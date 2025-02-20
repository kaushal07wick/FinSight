from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import pandas as pd

# Proxy setup (if needed)
proxy_server_ip = "http=47.251.122.81:8888"

# Custom User-Agent to avoid detection
custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

# Setup Selenium WebDriver
options = Options()
options.add_argument(f"--proxy-server={proxy_server_ip}")  # Use proxy if required
options.add_argument(f"--user-agent={custom_user_agent}")  # Bypass bot detection
options.add_argument("--blink-settings=imagesEnabled=false")  # Disable images for speed
options.add_argument("--ignore-certificate-errors")  # Ignore SSL errors
options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection
options.add_experimental_option("detach", True)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize Chrome driver
service = Service()
driver = webdriver.Chrome(service=service, options=options)

# Target URL
url = "https://seekingalpha.com/symbol/JPM/earnings/transcripts"

driver.get(url)
time.sleep(5)  # Initial wait to load the page

# Wait for transcript links to be clickable
wait = WebDriverWait(driver, 10)
elements = wait.until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, "a[data-test-id*='post-list-item-title']")
))

# Filter for visible elements
vis_ele = list(filter(lambda e: e.is_displayed(), elements))

# Extracting links
links = [el.get_attribute("href") for el in vis_ele[:10]]

if links:
    print(f"Found {len(links)} transcript links:")
    for link in links:
        print(link)
else:
    print("No transcript links found.")

transcript_data = []

# Scrape each link
for link in links:
    print(f"Clicking and scraping: {link}")
    driver.get(link)
    time.sleep(5)  # Allow the page to load after click

    # Get the full page source after the page has loaded
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Extract transcript text
    article = soup.find("article", class_="container")  # Update with the correct class for article section

    if article:
        # Extract title from the article header (if available)
        title_element = article.find("h1")
        title = title_element.get_text(strip=True) if title_element else "No Title Found"

        # Extract transcript text (assuming it's within the <p> tags)
        transcript_text = "\n".join([p.get_text() for p in article.find_all("p")]) if article else "No transcript available."
    else:
        title = "No Title Found"
        transcript_text = "No transcript available."

    print(f"Title: {title}")
    print(f"Transcript Text: {transcript_text}")

    # Append data to transcript_data list
    transcript_data.append({
        "title": title,
        "transcript_text": transcript_text
    })

# Save to DataFrame
if transcript_data:
    df = pd.DataFrame(transcript_data)
    df.to_csv("earnings_transcripts.csv", index=False, encoding="utf-8")
    print("Scraping complete. Data saved to earnings_transcripts.csv")
else:
    print("No transcripts found.")
    
# Quit the driver after scraping
driver.quit()
