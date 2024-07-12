# SumaRI
# SumarAI - YouTube Video Summarizer

SumarAI is a Python application that summarizes YouTube video transcripts using the Groq API. This project uses `tkinter` and `customtkinter` for the GUI, `PIL` for image handling, and `YouTubeTranscriptApi` for fetching transcripts.

## Features

- Fetches and displays YouTube video thumbnails.
- Retrieves video transcripts.
- Summarizes transcripts to highlight the main points.

## Requirements

- Python 3.6 or higher

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Nesbesss/SumaRI.git
    cd SumaRI
    ```

2. Create a virtual environment and activate it (not necessary):

    ```bash
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```
4. Set up your Groq API key:
 ```bash 
vi summarai.py then save it #windows notepad summarai.py 
```
    Replace `"Api_key_here"` in the script with your actual API key from Groq. to get one go to https://console.groq.com/keys its free

## Usage

1. Run the application:

    ```bash
    python summarai.py
    ```

2. Enter a YouTube video ID in the input field and click the "Summarize" button.

3. The application will fetch the video thumbnail, retrieve the transcript, and provide a summary of the main points.

## Example

- **Input:** YouTube Video ID: `72Q4g3V8woc`
- **Output:** Displayed video thumbnail and summary of the video transcript.

## Contributing

If you would like to contribute, please fork the repository and use a feature branch. Pull requests are welcome.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


