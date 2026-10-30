import datetime

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# Ask for the artist and song names.
artist = input("Artist name: ").strip()
song = input("Song name: ").strip()


# Replace spaces with hyphens and remove leading/trailing whitespace.
artist = artist.replace(" ", "-")
song = song.replace(" ", "-")

# Build the Genius lyrics URL.
url = f"https://genius.com/{quote(artist, safe='-')}-{quote(song, safe='-')}-lyrics"
# Helper function to append logs with a timestamp to a file
def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("genius_scrapper_debug_log.txt", "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")

log_message(f"Starting request to URL: {url}")

# Modern scraping requires headers or websites like Genius may reject the connection
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers)
    log_message(f"Response received. Status code: {response.status_code}")
    
    if response.ok:
        log_message("Parsing HTML content with BeautifulSoup...")
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Genius often splits lyrics across multiple matching containers
        log_message("Searching for elements matching 'data-lyrics-container=true'...")
        lyrics_containers = soup.find_all("div", attrs={"data-lyrics-container": "true"})
        
        if lyrics_containers:
            log_message(f"Success! Found {len(lyrics_containers)} lyrics container(s).")
            
            # Combine the text from all matched lyric divs
            full_lyrics = ""
            for container in lyrics_containers:
                full_lyrics += container.get_text(separator="\n") + "\n"
            
            # Print the actual final output to the console
            print(full_lyrics.strip())
            log_message("Lyrics successfully extracted and printed to console.")
        else:
            log_message("Warning: Request was successful but no divs matched 'data-lyrics-container=true'.")
            
    else:
        log_message(f"Error: Server returned bad status code ({response.status_code})")

except Exception as e:
    log_message(f"Critical Exception caught during execution: {str(e)}")
