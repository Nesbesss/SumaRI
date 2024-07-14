import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from groq import Groq
import requests
from bs4 import BeautifulSoup
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

def get_video_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_manually_created_transcript(['en', 'nl', 'fr', 'de', 'es', 'it'])
        return " ".join([entry['text'] for entry in transcript.fetch()])
    except TranscriptsDisabled:
        print("Transcripts are disabled for this video.")
        return None
    except NoTranscriptFound:
        print("No manually created transcript found.")
        try:
            transcript = transcript_list.find_generated_transcript(['en', 'nl', 'fr', 'de', 'es', 'it'])
            return " ".join([entry['text'] for entry in transcript.fetch()])
        except NoTranscriptFound:
            print("No generated transcript found.")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_website_text(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text from common HTML elements
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text() for p in paragraphs])

        # Optionally, add more elements if needed (e.g., headings)
        return text
    except Exception as e:
        print(f"An error occurred while fetching website content: {e}")
        return None

def summarize_text(text):
    max_chars = 10000
    truncated_text = text[:max_chars] + ("..." if len(text) > max_chars else "")
    
    prompt = (f"Provide a detailed summary of the following content. "
              f"Include the following sections:\n\n"
              f"1. 🎯 Overall Summary (2-3 paragraphs)\n"
              f"2. 📌 Main Points (5-7 bullet points)\n"
              f"3. 🌟 Key Highlights (3-5 specific moments or ideas)\n"
              f"4. 💡 Important Insights (2-3 paragraphs on the significance of the content)\n"
              f"5. 🔑 Key Concepts (list of 5-7 terms or ideas with brief explanations)\n"
              f"6. 🤔 Thought-Provoking Questions (3-5 questions for further reflection)\n"
              f"7. 📊 Content Structure (brief overview of how the content is organized)\n"
              f"8. 🎭 Tone and Style (1 paragraph describing the author's approach)\n"
              f"9. 🎨 Visual Elements (if mentioned in the content, describe any significant visual aids)\n"
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

def answer_question(summary, question):
    prompt = f"""Based on the following summary, please answer the question:

Summary:
{summary}

Question: {question}

Please provide a concise and accurate answer based solely on the information given in the summary."""

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
                max_tokens=300,
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

def summarize_thread(url, is_youtube):
    update_status("📥 Retrieving content...")
    if is_youtube:
        video_id = get_video_id(url)
        transcript = get_video_transcript(video_id)
        thumbnail = get_thumbnail(video_id)
        thumbnail_label.configure(image=thumbnail)
        thumbnail_label.image = thumbnail
    else:
        transcript = get_website_text(url)
    
    if transcript:
        update_status("🧠 Analyzing and summarizing... This may take a few moments.")
        try:
            summary = summarize_text(transcript)
            summary_text.configure(state="normal")
            summary_text.delete("1.0", tk.END)
            summary_text.insert(tk.END, summary)
            summary_text.configure(state="disabled")
            update_status("✅ Summary complete! You can now ask questions about the summary.")
            question_frame.pack(side="right", fill="both", expand=True)
            ask_button.configure(state="normal")
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
        summary_text.insert(tk.END, "❌ Failed to retrieve the content.")
        summary_text.configure(state="disabled")
        update_status("Failed to retrieve content.")
    progress_bar.stop()
    progress_bar.pack_forget()
    summarize_button.configure(state="normal")

def start_summarize():
    url = url_entry.get()
    if not url:
        tk.messagebox.showerror("Error", "Please enter a valid URL.")
        return
    
    is_youtube = bool(get_video_id(url))
    
    try:
        if is_youtube:
            thumbnail = get_thumbnail(get_video_id(url))
            thumbnail_label.configure(image=thumbnail)
            thumbnail_label.image = thumbnail
        else:
            thumbnail_label.configure(image="")
            thumbnail_label.image = None
        
        summary_text.configure(state="normal")
        summary_text.delete("1.0", tk.END)
        summary_text.insert(tk.END, "🔍 Analyzing content... Please wait.")
        summary_text.configure(state="disabled")
        progress_bar.pack(pady=(0, 10))
        progress_bar.start()
        summarize_button.configure(state="disabled")
        ask_button.configure(state="disabled")
        answer_text.configure(state="normal")
        answer_text.delete("1.0", tk.END)
        answer_text.configure(state="disabled")
        
        threading.Thread(target=summarize_thread, args=(url, is_youtube), daemon=True).start()
    except Exception as e:
        tk.messagebox.showerror("Error", str(e))

def ask_question():
    question = question_entry.get()
    if not question:
        tk.messagebox.showerror("Error", "Please enter a question.")
        return
    
    summary = summary_text.get("1.0", tk.END)
    update_status("🤔 Thinking about your question...")
    ask_button.configure(state="disabled")
    
    def answer_thread():
        try:
            answer = answer_question(summary, question)
            answer_text.configure(state="normal")
            answer_text.delete("1.0", tk.END)
            answer_text.insert(tk.END, answer)
            answer_text.configure(state="disabled")
            update_status("✅ Question answered!")
        except Exception as e:
            error_message = f"❌ An error occurred while answering the question: {str(e)}"
            answer_text.configure(state="normal")
            answer_text.delete("1.0", tk.END)
            answer_text.insert(tk.END, error_message)
            answer_text.configure(state="disabled")
            update_status("Error occurred while answering the question.")
        finally:
            ask_button.configure(state="normal")
    
    threading.Thread(target=answer_thread, daemon=True).start()

# Set up the main window
root = ctk.CTk()
root.title("SummarAI - Advanced YouTube Video and Website Summarizer with Q&A")
root.geometry("1200x800")  # Increased width to accommodate side-by-side layout

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
main_frame = ctk.CTkFrame(root)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

input_frame = ctk.CTkFrame(main_frame)
input_frame.pack(fill="x", padx=10, pady=10)

ctk.CTkLabel(input_frame, text="🔗 Enter YouTube Video or Website URL:", font=("Arial", 18, "bold")).pack(side="left", padx=(0, 10))
url_entry = ctk.CTkEntry(input_frame, width=400, height=40, font=("Arial", 14))
url_entry.pack(side="left", padx=(0, 10))

summarize_button = ctk.CTkButton(input_frame, text="🚀 Generate Summary", command=start_summarize, font=("Arial", 16, "bold"), height=40)
summarize_button.pack(side="left")

thumbnail_label = ctk.CTkLabel(main_frame, text="")
thumbnail_label.pack(pady=(0, 10))

content_frame = ctk.CTkFrame(main_frame)
content_frame.pack(fill="both", expand=True)

summary_frame = ctk.CTkFrame(content_frame)
summary_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

summary_text = ctk.CTkTextbox(summary_frame, wrap="word", width=600, height=400, font=("Arial", 12))
summary_text.pack(fill="both", expand=True)
summary_text.configure(state="disabled")

question_frame = ctk.CTkFrame(content_frame)
question_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
question_frame.pack_forget()  # Initially hidden

ctk.CTkLabel(question_frame, text="❓ Ask a question about the summary:", font=("Arial", 16, "bold")).pack(pady=(0, 5))
question_entry = ctk.CTkEntry(question_frame, width=400, height=40, font=("Arial", 14))
question_entry.pack(pady=(0, 10))

ask_button = ctk.CTkButton(question_frame, text="🔍 Ask Question", command=ask_question, font=("Arial", 14, "bold"), height=40)
ask_button.pack(pady=(0, 10))

answer_text = ctk.CTkTextbox(question_frame, wrap="word", width=400, height=300, font=("Arial", 12))
answer_text.pack(fill="both", expand=True, pady=(0, 10))
answer_text.configure(state="disabled")

status_frame = ctk.CTkFrame(main_frame)
status_frame.pack(fill="x", padx=10, pady=10)

status_label = ctk.CTkLabel(status_frame, text="", font=("Arial", 14, "italic"))
status_label.pack(side="left")

progress_bar = ctk.CTkProgressBar(status_frame, mode="indeterminate", width=200)
progress_bar.pack(side="right")

root.mainloop()
