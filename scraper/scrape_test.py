import json
from bs4 import BeautifulSoup

# Sample API response (in JSON format)
api_response = {
    "html": """
    <div class="page" data-pagenum="1">
        <a data-track-category="quotepage_transcripts" data-track-action="foolcom_quotepage_click"
           data-source="foolcom_quotepage_click" data-track-link="JPMorgan Chase (JPM) Q4 2024 Earnings Call Transcript"
           href="/earnings/call-transcripts/2025/01/15/jpmorgan-chase-jpm-q4-2024-earnings-call-transcrip/"
           class="block border-b border-gray-300 hover-trigger md:items-center text-gray-1100 hover:text-black py-12px">
            <h3 class="mb-6 font-medium hover-target-cyan-700 mt-2px text-h5">JPMorgan Chase (JPM) Q4 2024 Earnings Call Transcript</h3>
            <p class="text-gray-800 mb-0px">JPM earnings call for the period ending December 31, 2024.</p>
            <div class="text-sm text-gray-800 mb-2px">
                Motley Fool Transcribing | Jan 15, 2025
            </div>
        </a>
        <a data-track-category="quotepage_transcripts" data-track-action="foolcom_quotepage_click"
           data-source="foolcom_quotepage_click" data-track-link="JPMorgan Chase (JPM) Q3 2024 Earnings Call Transcript"
           href="/earnings/call-transcripts/2024/10/11/jpmorgan-chase-jpm-q3-2024-earnings-call-transcrip/"
           class="block border-b border-gray-300 hover-trigger md:items-center text-gray-1100 hover:text-black py-12px">
            <h3 class="mb-6 font-medium hover-target-cyan-700 mt-2px text-h5">JPMorgan Chase (JPM) Q3 2024 Earnings Call Transcript</h3>
            <p class="text-gray-800 mb-0px">JPM earnings call for the period ending September 30, 2024.</p>
            <div class="text-sm text-gray-800 mb-2px">
                Motley Fool Transcribing | Oct 11, 2024
            </div>
        </a>
    </div>
    """
}

# Function to extract transcript links from the HTML content
def extract_transcript_links_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    # Find all the <a> tags and extract their href attribute if it contains 'earnings/call-transcripts'
    links = [a['href'] for a in soup.find_all('a', href=True) if 'earnings/call-transcripts' in a['href']]
    return links

# Extract the HTML content from the API response
html_content = api_response['html']

# Get all the transcript links
transcript_links = extract_transcript_links_from_html(html_content)

# Print the full URLs of the transcripts (prepend the base URL)
base_url = "https://www.fool.com"
full_links = [base_url + link for link in transcript_links]

# Output the full links
for link in full_links:
    print(link)
