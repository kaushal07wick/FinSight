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
proxy_server_ip = "http=3.12.144.146:3128"

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
url = "https://www.fool.com/quote/nyse/jpm/"
driver.get(url)
time.sleep(5)  # Allow time for the page to load

# Wait for transcript links to appear
wait = WebDriverWait(driver, 10)
elements = wait.until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, "a[data-track-link*='Earnings Call Transcript']")
))

# Extract the first 3 visible links
visible_links = [el.get_attribute("href") for el in elements if el.is_displayed()][:4]

# Ensure we found at least 3 links
if len(visible_links) < 3:
    print("Warning: Less than 3 transcript links found!")

# List to store transcripts
transcript_data = []

# Function to click "Load More" button 3 times before scraping
def load_more_transcripts():
    click_count = 0
    while click_count < 3:  # Click "Load More" 3 times
        try:
            # Locate the "Load More" button
            load_more_button = driver.find_element(By.CSS_SELECTOR, "button.load-more-button")

            # Click the "Load More" button
            load_more_button.click()
            time.sleep(5)  # Wait for new content to load

            # Check if new transcripts are visible
            elements = driver.find_elements(By.CSS_SELECTOR, "a[data-test-id*='post-list-item-title']")
            new_links = [el.get_attribute("href") for el in elements if el.is_displayed()]
            
            if new_links:
                print(f"Found {len(new_links)} new transcript links after clicking 'Load More'.")
                visible_links.extend(new_links)  # Add new links to the list
            else:
                print("No more new transcript links.")
                break  # Exit loop if no new links are found

            click_count += 1  # Increment the click count
        except Exception as e:
            print(f"Error while clicking 'Load More': {e}")
            break  # Exit loop if there's an error (e.g., no more "Load More" button)

# Call function to load more transcripts
load_more_transcripts()

# Scrape each earnings call transcript after all the links are gathered
for link in visible_links:
    print(f"Scraping transcript: {link}")
    driver.get(link)
    time.sleep(5)  # Wait for page to load

    # Parse page content
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Extract title
    title_element = soup.find("h1")
    title = title_element.get_text(strip=True) if title_element else "No Title Found"

    # Extract transcript text
    transcript_div = soup.find("div", class_="main-container")
    if transcript_div:
        transcript_text = "\n".join([p.get_text() for p in transcript_div.find_all("p")])
    else:
        transcript_text = "No transcript available."

    # Store the data
    transcript_data.append({"title": title, "transcript_text": transcript_text})

# Close the browser
driver.quit()

# Save results to CSV
df = pd.DataFrame(transcript_data)
df.to_csv("jpm_earnings_transcripts.csv", index=False, encoding="utf-8")

print("✅ Scraping complete! Data saved to jpm_earnings_transcripts.csv.")
