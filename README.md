# SumaRI
# SumarAI - YouTube Video and Website Summarizer

SumarAI is a Python application that summarizes YouTube video transcripts and website content using the Groq API. This project uses `tkinter` and `customtkinter` for the GUI, `PIL` for image handling, `YouTubeTranscriptApi` for fetching video transcripts, and `BeautifulSoup` for extracting website text.

## Features

- Fetches and displays YouTube video thumbnails.
- Retrieves and summarizes YouTube video transcripts.
- Summarizes website content to highlight the main points.
- Allows users to ask questions about the generated summary.

## Requirements

- Python 3.6 or higher

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Nesbesss/SumaRI.git
    cd SumaRI
    ```

2. Create a virtual environment and activate it (optional):

    ```bash
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip3 install -r requirements.txt 
    ```

4. Set up your Groq API key:

    ```bash 
    vi summarai.py  # On Windows, use notepad summarai.py 
    ```
    Replace `"Your_api_key_here"` in the script with your actual API key from Groq. To get one, go to https://console.groq.com/keys. It's free.

## Usage

1. Run the application:

    ```bash
    python summarai.py
    ```

2. Enter a YouTube video URL or website URL in the input field and click the "Generate Summary" button.

3. The application will fetch the video thumbnail (for YouTube), retrieve the transcript (for YouTube), and provide a summary of the main points.

4. You can then enter questions about the summary in the input field and click the "Ask Question" button to get answers based on the summarized content.

## Example

- **Input:** YouTube Video URL: `https://www.youtube.com/watch?v=72Q4g3V8woc` or Website URL: `https://example.com`
- **Output:** Displayed video thumbnail (for YouTube) and summary of the video transcript or website content.

## Contributing

If you would like to contribute, please fork the repository and use a feature branch. Pull requests are welcome.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
