
# Import the libraries needed for the program to work.
import datetime  # Gets the current date and time for logging.
import requests  # Sends HTTP requests to websites and retrieves their responses.
from bs4 import BeautifulSoup  # Parses HTML so we can find specific elements on a webpage.


# Build the URL for the Genius lyrics page.
# Genius URLs generally follow this format:
# https://genius.com/artist-name-song-name-lyrics

from urllib.parse import quote

# Ask for the artist and song names.
artist = input("Artist name: ").strip()
song = input("Song name: ").strip()

# Convert the names into URL-friendly text.
# Replace spaces with hyphens and remove leading/trailing whitespace.
artist = artist.replace(" ", "-")
song = song.replace(" ", "-")

# Build the Genius lyrics URL.
# quote() safely encodes characters that have special meanings in URLs.
url = f"https://genius.com/{quote(artist, safe='-')}-{quote(song, safe='-')}-lyrics"

# Display the generated URL so the user can check it.
print(f"URL: {url}")


# Define a function that writes a message to a debug log file.
# A debug log helps us understand what the program did, especially
# when something goes wrong and there is no useful error in the console.
def log_message(message):

    # Get the current date and time.
    # strftime() formats it into a readable string:
    # YYYY-MM-DD HH:MM:SS
    # Example: 2026-10-30 11:55:00
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Open the log file in append mode ("a").
    # Append mode adds new messages to the end of the file instead
    # of deleting the messages from previous runs.
    #
    # encoding="utf-8" allows the file to store a wide range of characters.
    # The "with" statement automatically closes the file when finished.
    with open("genius_scrapper_debug_log.txt", "a", encoding="utf-8") as file:

        # Write the timestamp and message to the file.
        # \n starts a new line so each log message appears separately.
        file.write(f"[{timestamp}] {message}\n")


# Record that the program is starting a request.
# Including the URL makes it easier to check which page the program tried to access.
log_message(f"Starting request to URL: {url}")


# Create a dictionary containing HTTP request headers.
# Headers provide additional information about the request being sent
# to a website.
headers = {
    # User-Agent identifies the software making the request.
    #
    # Some websites treat requests from simple scripts differently from
    # requests made by regular browsers. This value identifies the request
    # as coming from a browser-like client.
    #
    # Important: A User-Agent does not guarantee that the website will
    # allow the request.
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# Start a try block so that errors during the request or HTML processing
# can be caught instead of immediately terminating the program.
try:

    # Send an HTTP GET request to the Genius page.
    #
    # A GET request asks the server to return a resource, in this case
    # the webpage containing the lyrics.
    #
    # headers=headers attaches our custom headers to the request.
    #
    # requests.get() returns a Response object containing information
    # about the server's reply, including its status code and page content.
    response = requests.get(url, headers=headers)

    # Record the HTTP status code returned by the server.
    #
    # Common status codes include:
    # 200 = The request succeeded.
    # 403 = The server refused access.
    # 404 = The requested page was not found.
    # 429 = Too many requests were sent.
    #
    # Logging this helps identify problems with the request.
    log_message(f"Response received. Status code: {response.status_code}")


    # Check whether the HTTP response indicates success.
    # response.ok is True for status codes from 200 through 399.
    # It does not guarantee that the expected lyrics are present.
    if response.ok:

        # Record that the program is about to process the webpage.
        log_message("Parsing HTML content with BeautifulSoup...")

        # Parse the HTML source returned by Genius.
        #
        # response.text contains the webpage's HTML as a string.
        # BeautifulSoup organizes that HTML into a structure that lets
        # us search for elements, inspect their attributes, and extract text.
        #
        # "html.parser" is Python's built-in HTML parser.
        soup = BeautifulSoup(response.text, "html.parser")


        # Record which HTML elements the program is going to search for.
        log_message("Searching for elements matching 'data-lyrics-container=true'...")


        # Find every <div> element whose data-lyrics-container attribute
        # has the value "true".
        #
        # Genius uses these containers to hold sections of song lyrics.
        #
        # find_all() returns a list of matching elements because the lyrics
        # may be split across multiple containers instead of appearing
        # inside one large element.
        #
        # Example HTML:
        # <div data-lyrics-container="true">
        #     First line of lyrics
        # </div>
        #
        # The result is stored in lyrics_containers.
        lyrics_containers = soup.find_all(
            "div",
            attrs={"data-lyrics-container": "true"}
        )


        # Check whether any matching lyric containers were found.
        # An empty list means the expected elements were not found.
        if lyrics_containers:

            # Record how many containers were found.
            # This can help determine whether the page was parsed correctly.
            log_message(
                f"Success! Found {len(lyrics_containers)} lyrics container(s)."
            )


            # Create an empty string that will hold the complete lyrics.
            full_lyrics = ""


            # Loop through every matching lyrics container.
            # Each container may contain a different section of the song.
            for container in lyrics_containers:

                # Extract all readable text from the current container.
                #
                # get_text() removes the HTML tags and returns the text
                # contained inside the element.
                #
                # separator="\n" inserts a newline between separate text
                # elements inside the container. This helps preserve
                # line breaks between lyric lines.
                #
                # The final "\n" adds another newline after each container
                # to separate different sections of lyrics.
                #
                # += appends the extracted text to the existing string
                # instead of replacing what was already collected.
                full_lyrics += container.get_text(separator="\n") + "\n"


            # Print the completed lyrics to the terminal.
            #
            # strip() removes whitespace from the beginning and end
            # of the entire string, including unnecessary outer newlines.
            #
            # The original internal line breaks are preserved.
            print(full_lyrics.strip())


            # Record that the lyrics were extracted and printed.
            log_message("Lyrics successfully extracted and printed to console.")

        else:

            # The HTTP request succeeded, but BeautifulSoup could not find
            # any elements matching the expected lyrics-container attribute.
            #
            # Possible reasons include:
            # - The URL points to a page without lyrics.
            # - The page structure has changed.
            # - Genius returned a page that does not contain the lyrics.
            # - The lyrics are unavailable or were not included in the HTML.
            log_message(
                "Warning: Request was successful but no divs matched "
                "'data-lyrics-container=true'."
            )

    else:

        # The server returned a status code outside the successful range.
        # Record the code so the problem can be investigated later.
        log_message(
            f"Error: Server returned bad status code ({response.status_code})"
        )


# Handle exceptions raised while executing the code inside the try block.
# For example, requests.get() might fail because of a network connection
# problem, or BeautifulSoup processing might encounter an unexpected error.
except Exception as e:

    # Convert the exception into a readable string and write it to the log.
    #
    # str(e) usually contains a description of the error, which helps
    # identify what went wrong.
    #
    # Note that this logs the error rather than printing it to the console.
    log_message(f"Critical Exception caught during execution: {str(e)}")

