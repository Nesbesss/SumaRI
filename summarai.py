import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from groq import Groq
import requests
from io import BytesIO
import threading
import time
import re

# Set up Groq client with the API key
client = Groq(
    api_key="Your_api_key_here"  # Replace with your actual API key
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def get_video_id(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    match = re.search(youtube_regex, url)
    return match.group(6) if match else None

def get_video_transcript(video_id, language_code='en'):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript([language_code])
        return " ".join([entry['text'] for entry in transcript.fetch()])
    except TranscriptsDisabled:
        print("Transcripts are disabled for this video.")
        return None
    except NoTranscriptFound:
        print(f"No transcript found for language code: {language_code}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def summarize_text(text):
    max_chars = 10000
    truncated_text = text[:max_chars] + ("..." if len(text) > max_chars else "")
    
    prompt = (f"Provide a detailed summary of the following YouTube video transcript. "
              f"Include the following sections:\n\n"
              f"1. 🎯 Overall Summary (2-3 paragraphs)\n"
              f"2. 📌 Main Points (5-7 bullet points)\n"
              f"3. 🌟 Key Highlights (3-5 specific moments or ideas)\n"
              f"4. 💡 Important Insights (2-3 paragraphs on the significance of the content)\n"
              f"5. 🔑 Key Concepts (list of 5-7 terms or ideas with brief explanations)\n"
              f"6. 🤔 Thought-Provoking Questions (3-5 questions for further reflection)\n"
              f"7. 📊 Content Structure (brief overview of how the video is organized)\n"
              f"8. 🎭 Tone and Style (1 paragraph describing the presenter's approach)\n"
              f"9. 🎨 Visual Elements (if mentioned in the transcript, describe any significant visual aids)\n"
              f"10. 📚 Further Reading (suggest 2-3 related topics for additional research)\n\n"
              f"Aim for a comprehensive summary of around 1000 words:\n\n{truncated_text}\n\nDetailed summary:")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="mixtral-8x7b-32768",
                max_tokens=1500,
            )
            
            return chat_completion.choices[0].message.content
        except Exception as e:
            if "rate_limit_exceeded" in str(e) and attempt < max_retries - 1:
                wait_time = 2 ** attempt
                update_status(f"Rate limit reached. Waiting for {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                raise e

def get_thumbnail(video_id):
    url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.thumbnail((200, 150))  # Smaller thumbnail size
    return ImageTk.PhotoImage(img)

def update_status(message):
    status_label.configure(text=message)
    root.update_idletasks()

def summarize_thread(video_id, language_code):
    update_status("📥 Retrieving video transcript...")
    transcript = get_video_transcript(video_id, language_code)
    if transcript:
        update_status("🧠 Analyzing and summarizing... This may take a few moments.")
        try:
            summary = summarize_text(transcript)
            summary_text.configure(state="normal")
            summary_text.delete("1.0", tk.END)
            summary_text.insert(tk.END, summary)
            summary_text.configure(state="disabled")
            update_status("✅ Summary complete! Scroll down to read the full analysis.")
        except Exception as e:
            error_message = f"❌ An error occurred while summarizing: {str(e)}"
            summary_text.configure(state="normal")
            summary_text.delete("1.0", tk.END)
            summary_text.insert(tk.END, error_message)
            summary_text.configure(state="disabled")
            update_status("Error occurred during summarization.")
    else:
        summary_text.configure(state="normal")
        summary_text.delete("1.0", tk.END)
        summary_text.insert(tk.END, "❌ Failed to retrieve the video transcript.")
        summary_text.configure(state="disabled")
        update_status("Failed to retrieve transcript.")
    progress_bar.stop()
    progress_bar.pack_forget()
    summarize_button.configure(state="normal")

def start_summarize():
    video_url = video_id_entry.get()
    language_code = language_entry.get()
    video_id = get_video_id(video_url)
    if not video_id:
        tk.messagebox.showerror("Error", "Please enter a valid YouTube Video URL.")
        return
    
    try:
        thumbnail = get_thumbnail(video_id)
        thumbnail_label.configure(image=thumbnail)
        thumbnail_label.image = thumbnail
        summary_text.configure(state="normal")
        summary_text.delete("1.0", tk.END)
        summary_text.insert(tk.END, "🔍 Analyzing video content... Please wait.")
        summary_text.configure(state="disabled")
        progress_bar.pack(pady=(0, 10))
        progress_bar.start()
        summarize_button.configure(state="disabled")
        
        threading.Thread(target=summarize_thread, args=(video_id, language_code), daemon=True).start()
    except Exception as e:
        tk.messagebox.showerror("Error", str(e))

# Set up the main window
root = ctk.CTk()
root.title("SummarAI - Advanced YouTube Video Summarizer")
root.geometry("1000x800")  # Increased width and height

# ASCII art logo with color
logo_text = """
\033[94m ____                                  ___  ___\033[0m
\033[94m/ ___|  _   _  _ __ ___   _ __ ___    / _ \|_ _|\033[0m
\033[94m\___ \ | | | || '_ ` _ \ | '_ ` _ \  | | | || | \033[0m
\033[94m ___) || |_| || | | | | || | | | | | | |_| || | \033[0m
\033[94m|____/  \__,_||_| |_| |_||_| |_| |_|  \___/|___|\033[0m
"""

# Add stylized logo to the top of the window
logo_label = ctk.CTkLabel(root, text=logo_text, font=("Courier", 16, "bold"), text_color="blue")
logo_label.pack(pady=(20, 10))

# Create and place widgets
frame = ctk.CTkFrame(root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

ctk.CTkLabel(frame, text="🎥 Enter YouTube Video URL:", font=("Arial", 18, "bold")).pack(pady=(0, 5))
video_id_entry = ctk.CTkEntry(frame, width=400, height=40, font=("Arial", 14))
video_id_entry.pack(pady=(0, 15))

ctk.CTkLabel(frame, text="🌐 Enter Language Code (e.g., 'en' for English, 'nl' for Dutch):", font=("Arial", 18, "bold")).pack(pady=(0, 5))
language_entry = ctk.CTkEntry(frame, width=400, height=40, font=("Arial", 14))
language_entry.pack(pady=(0, 15))

summarize_button = ctk.CTkButton(frame, text="🚀 Generate Comprehensive Summary", command=start_summarize, font=("Arial", 16, "bold"), height=50)
summarize_button.pack(pady=(0, 20))

thumbnail_label = ctk.CTkLabel(frame, text="")
thumbnail_label.pack(pady=(0, 20))

summary_text = ctk.CTkTextbox(frame, wrap="word", width=900, height=600, font=("Arial", 12))  # Larger text box
summary_text.pack(pady=(0, 20))
summary_text.configure(state="disabled")

status_label = ctk.CTkLabel(frame, text="", font=("Arial", 14, "italic"))
status_label.pack(pady=(0, 10))

progress_bar = ctk.CTkProgressBar(frame, mode="indeterminate", width=400)
# Don't pack the progress bar here, we'll pack it when needed

root.mainloop()
