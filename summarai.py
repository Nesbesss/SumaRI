import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq
import requests
from io import BytesIO
import threading
import time

# Set up Groq client with the API key
client = Groq(
    api_key="Your_api_key_here"  # Replace with your actual API key
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def summarize_text(text):
    # Truncate the text to reduce processing time
    max_chars = 5000
    truncated_text = text[:max_chars] + ("..." if len(text) > max_chars else "")
    
    prompt = (f"Provide a comprehensive summary of the following YouTube video transcript. "
              f"Include the following sections:\n"
              f"1. 📌 Main Points (3-5 bullet points)\n"
              f"2. 🌟 Highlights (2-3 key takeaways)\n"
              f"3. 💡 Important Insights (1-2 paragraphs)\n"
              f"4. 🔑 Key Concepts (list of 3-5 terms or ideas)\n\n"
              f"Keep the entire summary under 300 words:\n\n{truncated_text}\n\nComprehensive summary:")
    
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
                max_tokens=400,
            )
            
            return chat_completion.choices[0].message.content
        except Exception as e:
            if "rate_limit_exceeded" in str(e) and attempt < max_retries - 1:
                wait_time = 2 ** attempt
                update_status(f"Rate limit reached. Waiting for {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                raise e

# ... (rest of the functions remain the same)

def start_summarize():
    video_id = video_id_entry.get()
    if not video_id:
        tk.messagebox.showerror("Error", "Please enter a YouTube Video ID.")
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
        
        threading.Thread(target=summarize_thread, args=(video_id,), daemon=True).start()
    except Exception as e:
        tk.messagebox.showerror("Error", str(e))

# Set up the main window
root = ctk.CTk()
root.title("SummarAI - YouTube Video Summarizer")
root.geometry("800x800")  # Increased height to accommodate more text

# ASCII art logo
logo_text = """
 ____                           ___  ___
/ ___|  _   _  _ __ ___   __ _ |  _ \|_ _|
\___ \ | | | || '_ ` _ \ / _` || |_) || | 
 ___) || |_| || | | | | | (_| ||  _ < | | 
|____/  \__,_||_| |_| |_|\__,_||_| \_\___|
"""

# Add logo to the top of the window
logo_label = ctk.CTkLabel(root, text=logo_text, font=("Courier", 14), text_color="blue")
logo_label.pack(pady=(10, 20))

# Create and place widgets
frame = ctk.CTkFrame(root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

ctk.CTkLabel(frame, text="Enter YouTube Video ID:", font=("Arial", 16, "bold")).pack(pady=(0, 5))
video_id_entry = ctk.CTkEntry(frame, width=300)
video_id_entry.pack(pady=(0, 10))

summarize_button = ctk.CTkButton(frame, text="🚀 Summarize", command=start_summarize, font=("Arial", 14, "bold"))
summarize_button.pack(pady=(0, 10))

thumbnail_label = ctk.CTkLabel(frame, text="")
thumbnail_label.pack(pady=(0, 10))

summary_text = ctk.CTkTextbox(frame, wrap="word", width=700, height=400)  # Increased height
summary_text.pack(pady=(0, 10))
summary_text.configure(state="disabled")

status_label = ctk.CTkLabel(frame, text="", font=("Arial", 12, "italic"))
status_label.pack(pady=(0, 10))

progress_bar = ctk.CTkProgressBar(frame, mode="indeterminate", width=300)
# Don't pack the progress bar here, we'll pack it when needed

root.mainloop()
