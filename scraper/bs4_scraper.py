import requests
from bs4 import BeautifulSoup
import csv

# URL of the API response
url = "https://www.fool.com/dubs/ajax/quote/articles_by_page/204149/earnings_transcripts?page=1&per_page=24"

# Send the GET request to get the list of links
response = requests.get(url)

# Parse the JSON response
data = response.json()

# Extract the HTML content from the response
html_content = data["html"]

# Use BeautifulSoup with lxml parser to parse the HTML content
soup = BeautifulSoup(html_content, "lxml")

# Base URL to prepend to relative links
base_url = "https://www.fool.com"

# Find all <a> tags and extract the 'href' attributes
hrefs = [base_url + a['href'] if a['href'].startswith('/') else a['href'] for a in soup.find_all('a', href=True)]

# Open a CSV file to store the results
with open('main_jpm_transcripts.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Text"])  # Write header row
    
    # Now, let's scrape data from each of the links
    for link in hrefs:
        # Send a request to each link
        page_response = requests.get(link)
        
        # Parse the page HTML content with lxml parser
        page_soup = BeautifulSoup(page_response.text, 'lxml')
        
        # Extract the title (usually inside a <h1>, <h2>, or similar tag)
        title = page_soup.find('h1')  # Adjust this based on the actual title location
        title_text = title.get_text() if title else "No title found"
        
        # Extract the article content from 'article-body' div
        article_div = page_soup.find('div', class_='article-body')  # Ensure the correct class for content
        article_text = article_div.get_text() if article_div else "No article content found"
        
        # Write the title and text to the CSV file
        writer.writerow([title_text, article_text])

        print(f"Scraped content from: {link}")  # Print progress (optional)

print("Data has been saved to main_jpm_transcripts.csv")
