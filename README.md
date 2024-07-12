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
    git clone https://github.com/your-username/SumarAI.git
    cd SumarAI
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

    Ensure your `requirements.txt` file includes the following:

    ```
    tkinter
    customtkinter
    pillow
    youtube_transcript_api
    requests
    groq
    ```

4. Set up your Groq API key:

    Replace `"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"` in the script with your actual API key from Groq.

## Usage

1. Run the application:

    ```bash
    python summarai.py
    ```

2. Enter a YouTube video ID in the input field and click the "Summarize" button.

3. The application will fetch the video thumbnail, retrieve the transcript, and provide a summary of the main points.

## Example

- **Input:** YouTube Video ID: `dQw4w9WgXcQ`
- **Output:** Displayed video thumbnail and summary of the video transcript.

## Contributing

If you would like to contribute, please fork the repository and use a feature branch. Pull requests are welcome.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


