import os
import threading
import tkinter as tk
from gtts import gTTS
from tkinter import ttk, scrolledtext
import speech_recognition as sr
from playsound import playsound
from deep_translator import GoogleTranslator
from google.transliteration import transliterate_text
import datetime
import time
import pyttsx3

# --- UI Configuration ---
PRIMARY_DARK = "#2c3e50"  # Deep Prussian Blue
ACCENT_LIGHT = "#ecf0f1"  # Light Grey/Silver
TEXT_COLOR = "#ffffff"    # White
HIGHLIGHT_COLOR = "#3498db" # Peter River Blue
SUCCESS_COLOR = "#27ae60"  # Emerald Green
ERROR_COLOR = "#e74c3c"    # Alizarin Red
TRANSLITERATION_COLOR = "#f1c40f" # Sunflower Yellow
INFO_COLOR = "#95a5a6" # Grey for info messages
OFFLINE_PLAY_COLOR = "#8e44ad" # Amethyst Purple

FONT_FAMILY = "Segoe UI"
LARGE_FONT = (FONT_FAMILY, 16, 'bold')
MEDIUM_FONT = (FONT_FAMILY, 12)
SMALL_FONT = (FONT_FAMILY, 10, 'italic')
MICROPHONE_STATE_FONT = (FONT_FAMILY, 14, 'bold')

# Create an instance of Tkinter frame or window
win = tk.Tk()

# Set the geometry of tkinter frame
win.geometry("900x820")
win.title("EchoWrite: Real-Time Voice🎙️ Translator🔊") # Updated Title
win.configure(bg=PRIMARY_DARK)
icon = tk.PhotoImage(file="icon.png") #
win.iconphoto(False, icon)

# Apply a modern theme and custom styles for a luxurious look
style = ttk.Style()
style.theme_use('clam')

# General styles
style.configure('.', background=PRIMARY_DARK, foreground=TEXT_COLOR)
style.configure('TLabel', font=MEDIUM_FONT, foreground=TEXT_COLOR, background=PRIMARY_DARK)
style.configure('TButton', font=MEDIUM_FONT, background=HIGHLIGHT_COLOR, foreground=TEXT_COLOR, borderwidth=0, relief="flat", padding=(10, 5))
style.map('TButton',
          background=[('active', HIGHLIGHT_COLOR)],
          foreground=[('active', TEXT_COLOR)])

style.configure('TCombobox', font=MEDIUM_FONT, fieldbackground=ACCENT_LIGHT, background=PRIMARY_DARK, foreground='#333')
style.map('TCombobox',
          fieldbackground=[('readonly', ACCENT_LIGHT)],
          selectbackground=[('readonly', HIGHLIGHT_COLOR)],
          selectforeground=[('readonly', TEXT_COLOR)])

style.configure('ScrolledText', font=MEDIUM_FONT, borderwidth=1, relief="solid",
                background=ACCENT_LIGHT, foreground='#333',
                selectbackground=HIGHLIGHT_COLOR, selectforeground=TEXT_COLOR)

# Custom style for the main section frames for better visual separation
style.configure('Section.TFrame', background=PRIMARY_DARK, relief="flat", borderwidth=0)
style.configure('TextSection.TFrame', background=PRIMARY_DARK, relief="groove", borderwidth=1, bordercolor=HIGHLIGHT_COLOR)


# --- Widgets ---

# Input Text Section
input_frame = ttk.Frame(win, style='TextSection.TFrame')
input_frame.pack(pady=(15, 5), padx=30, fill='x')
ttk.Label(input_frame, text="Recognized Text 🗣️", font=LARGE_FONT, foreground=HIGHLIGHT_COLOR, background=PRIMARY_DARK).pack(pady=(10, 5))
input_text = scrolledtext.ScrolledText(input_frame, height=6, width=80, wrap=tk.WORD, state='disabled', relief="flat")
input_text.pack(pady=10, padx=15, fill='both', expand=True)

# Live Transliteration Display
live_transliteration_label = ttk.Label(win, text="Speak to see live transliteration...", font=(FONT_FAMILY, 16, 'italic'), foreground=TRANSLITERATION_COLOR, background=PRIMARY_DARK)
live_transliteration_label.pack(pady=(10, 5))
ttk.Label(win, text="Tip: Speak clearly and at a moderate pace for best live results.", font=SMALL_FONT, foreground=INFO_COLOR, background=PRIMARY_DARK).pack(pady=(0, 10))

# Microphone Status
mic_status_label = ttk.Label(win, text="🔴 Not Listening", font=MICROPHONE_STATE_FONT, foreground=ERROR_COLOR, background=PRIMARY_DARK)
mic_status_label.pack(pady=(5, 10))


# Output Text Section
output_frame = ttk.Frame(win, style='TextSection.TFrame')
output_frame.pack(pady=(15, 5), padx=30, fill='x')
ttk.Label(output_frame, text="Translated Text 🌐", font=LARGE_FONT, foreground=HIGHLIGHT_COLOR, background=PRIMARY_DARK).pack(pady=(10, 5))
output_text = scrolledtext.ScrolledText(output_frame, height=6, width=80, wrap=tk.WORD, state='disabled', relief="flat")
output_text.pack(pady=10, padx=15, fill='both', expand=True)

# Offline Playback Button
play_offline_button = ttk.Button(output_frame, text="Listen Offline 🔊", command=lambda: threading.Thread(target=play_offline_audio).start(),
                                 style='Offline.TButton')
play_offline_button.pack(pady=5, padx=15, anchor='e')
play_offline_button.config(state='disabled')
style.configure('Offline.TButton', background=OFFLINE_PLAY_COLOR, foreground=TEXT_COLOR)
style.map('Offline.TButton', background=[('active', '#7D3C98'), ('disabled', '#5f4d6d')])


# Language Selection Frame
lang_select_frame = ttk.Frame(win, style='Section.TFrame')
lang_select_frame.pack(pady=20)

language_codes = {
    "English": "en", "Hindi": "hi", "Bengali": "bn", "Spanish": "es", "Chinese (Simplified)": "zh-CN",
    "Russian": "ru", "Japanese": "ja", "Korean": "ko", "German": "de", "French": "fr",
    "Tamil": "ta", "Telugu": "te", "Kannada": "kn", "Gujarati": "gu", "Punjabi": "pa"
}
language_names = sorted(list(language_codes.keys()))

ttk.Label(lang_select_frame, text="Select Input Language:", font=MEDIUM_FONT).grid(row=0, column=0, padx=10, pady=5, sticky='w')
input_lang = ttk.Combobox(lang_select_frame, values=language_names, state="readonly", width=25)
def update_input_lang_code(event):
    selected_language_name = event.widget.get()
    selected_language_code = language_codes[selected_language_name]
    input_lang.set(selected_language_code)
    input_lang.set(selected_language_name)
input_lang.bind("<<ComboboxSelected>>", update_input_lang_code)
input_lang.set("English")
input_lang.grid(row=0, column=1, padx=10, pady=5, sticky='ew')

ttk.Label(lang_select_frame, text="Select Output Language:", font=MEDIUM_FONT).grid(row=1, column=0, padx=10, pady=5, sticky='w')
output_lang = ttk.Combobox(lang_select_frame, values=language_names, state="readonly", width=25)
def update_output_lang_code(event):
    selected_language_name = event.widget.get()
    selected_language_code = language_codes[selected_language_name]
    output_lang.set(selected_language_code)
    output_lang.set(selected_language_name)
output_lang.bind("<<ComboboxSelected>>", update_output_lang_code)
output_lang.set("Hindi")
output_lang.grid(row=1, column=1, padx=10, pady=5, sticky='ew')

# Main Control Button Frame
control_button_frame = ttk.Frame(win, style='Section.TFrame')
control_button_frame.pack(pady=20)

run_button = ttk.Button(control_button_frame, text="Start Translation ▶️", command=lambda: threading.Thread(target=run_translator).start())
run_button.grid(row=0, column=0, padx=10)

kill_button = ttk.Button(control_button_frame, text="Stop Translation ⏹️", command=lambda: threading.Thread(target=kill_execution).start())
kill_button.grid(row=0, column=1, padx=10)

process_now_button = ttk.Button(control_button_frame, text="Process Now ⏩", command=lambda: threading.Thread(target=trigger_immediate_processing).start())
process_now_button.grid(row=0, column=2, padx=10)

about_button = ttk.Button(control_button_frame, text="About ℹ️", command=lambda: threading.Thread(target=open_about_page).start())
about_button.grid(row=0, column=3, padx=10)


# --- Logic ---
keep_running = False
audio_source = None
recognizer_instance = sr.Recognizer()

current_audio_buffer_data = b''
immediate_process_flag = threading.Event()

tts_engine = None
try:
    tts_engine = pyttsx3.init()
except Exception as e:
    print(f"Warning: pyttsx3 engine initialization failed: {e}. Offline playback will not be available.")
    tts_engine = None

last_translated_text = ""

def update_microphone_status(status_text, color):
    win.after(0, lambda: mic_status_label.config(text=status_text, foreground=color))

def update_translation_loop():
    global keep_running, audio_source, recognizer_instance, current_audio_buffer_data, immediate_process_flag

    if audio_source is None:
        audio_source = sr.Microphone()

    with audio_source as source:
        update_microphone_status("🟡 Adjusting for ambient noise...", INFO_COLOR)
        print("🎙️ Adjusting for ambient noise...")
        try:
            recognizer_instance.adjust_for_ambient_noise(source, duration=1.5)
        except Exception as e:
            print(f"Error during noise adjustment: {e}")
            update_microphone_status(f"❌ Error: {e}", ERROR_COLOR)
            keep_running = False
            return

        update_microphone_status("🟢 Listening...", SUCCESS_COLOR)
        print("🎙️ Listening for speech...")
        
        last_speech_activity_time = time.time()
        
        while keep_running:
            if immediate_process_flag.is_set():
                immediate_process_flag.clear()
                if current_audio_buffer_data:
                    update_microphone_status("🟡 Processing (Manual Trigger)...", INFO_COLOR)
                    process_final_audio(sr.AudioData(current_audio_buffer_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH))
                    current_audio_buffer_data = b''
                    win.after(0, lambda: live_transliteration_label.config(text="Speak to see live transliteration...", foreground=TRANSLITERATION_COLOR))
                    update_microphone_status("🟢 Listening...", SUCCESS_COLOR)
                continue

            try:
                audio_chunk = recognizer_instance.listen(source, phrase_time_limit=3.0, timeout=8.0)
                current_audio_buffer_data += audio_chunk.frame_data
                
                current_audio_data_for_partial = sr.AudioData(current_audio_buffer_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)

                current_input_lang_code = language_codes.get(input_lang.get(), 'en')
                
                partial_results = recognizer_instance.recognize_google(current_audio_data_for_partial, language=current_input_lang_code, show_all=True)
                
                partial_text = ""
                if partial_results and isinstance(partial_results, dict) and 'alternative' in partial_results:
                    partial_text = partial_results['alternative'][0]['transcript']
                elif isinstance(partial_results, str):
                    partial_text = partial_results

                if partial_text:
                    last_speech_activity_time = time.time()

                    if current_input_lang_code not in ('auto', 'en'):
                        try:
                            transliterated_partial = transliterate_text(partial_text, lang_code=current_input_lang_code)
                            win.after(0, lambda t=transliterated_partial: live_transliteration_label.config(text=f"Live: {t}", foreground=TRANSLITERATION_COLOR))
                        except Exception as e:
                            win.after(0, lambda: live_transliteration_label.config(text=f"Transliteration Error: {e}", foreground=ERROR_COLOR))
                    else:
                        win.after(0, lambda t=partial_text: live_transliteration_label.config(text=f"Live: {t}", foreground=TRANSLITERATION_COLOR))
                else:
                    win.after(0, lambda: live_transliteration_label.config(text="...", foreground=INFO_COLOR))


            except sr.WaitTimeoutError:
                if current_audio_buffer_data:
                    update_microphone_status("🟡 Processing (End of Phrase)...", INFO_COLOR)
                    process_final_audio(sr.AudioData(current_audio_buffer_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH))
                    current_audio_buffer_data = b''
                    win.after(0, lambda: live_transliteration_label.config(text="Speak to see live transliteration...", foreground=TRANSLITERATION_COLOR))
                    update_microphone_status("🟢 Listening...", SUCCESS_COLOR)
                else:
                     win.after(0, lambda: live_transliteration_label.config(text="Speak to see live transliteration...", foreground=TRANSLITERATION_COLOR))
                     update_microphone_status("🟢 Listening...", SUCCESS_COLOR)
                
            except sr.UnknownValueError:
                win.after(0, lambda: live_transliteration_label.config(text="Could not understand this phrase segment...", foreground=ERROR_COLOR))
                print("❌ Sorry, couldn't understand partial audio segment.")
                
            except sr.RequestError as e:
                win.after(0, lambda: live_transliteration_label.config(text=f"Live API Error: {e}", foreground=ERROR_COLOR))
                print(f"❌ API request error during live recognition: {e}")
                update_microphone_status("❌ API Error!", ERROR_COLOR)
                keep_running = False
                break
            except Exception as e:
                print(f"An unexpected error occurred in live loop: {e}")
                update_microphone_status(f"❌ Unexpected Error: {e}", ERROR_COLOR)
                keep_running = False
                break
            
            time.sleep(0.01)

        if current_audio_buffer_data:
            update_microphone_status("🟡 Finalizing...", INFO_COLOR)
            process_final_audio(sr.AudioData(current_audio_buffer_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH))
        
    update_microphone_status("🔴 Not Listening", ERROR_COLOR)
    print("Translation loop stopped.")


def process_final_audio(audio_data):
    """Processes the accumulated audio data for final recognition and translation."""
    global keep_running, recognizer_instance, current_audio_buffer_data, last_translated_text
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    win.after(0, lambda: play_offline_button.config(state='disabled'))

    if not audio_data.frame_data:
        print("No audio data to process for final recognition.")
        return

    try:
        current_input_lang_code = language_codes.get(input_lang.get(), 'en')
        speech_text = recognizer_instance.recognize_google(audio_data, language=current_input_lang_code)
        
        win.after(0, lambda: input_text.config(state='normal'))
        win.after(0, lambda: input_text.insert(tk.END, f"[{timestamp}] You Said: {speech_text}\n"))
        win.after(0, lambda: input_text.see(tk.END))
        win.after(0, lambda: input_text.config(state='disabled'))
        
        with open("voice_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] Recognized: {speech_text}\n")
        
        win.after(0, lambda: live_transliteration_label.config(text="Processing final recognition...", foreground=INFO_COLOR))

        if speech_text.lower() in {'exit', 'stop', 'quit'}:
            keep_running = False
            print("✅ Translation stopped by user.")
            win.after(0, lambda: output_text.config(state='normal'))
            win.after(0, lambda: output_text.insert(tk.END, f"[{timestamp}] Translation stopped by user.\n"))
            win.after(0, lambda: output_text.see(tk.END))
            win.after(0, lambda: output_text.config(state='disabled'))
            win.after(0, lambda: live_transliteration_label.config(text="Speak to see live transliteration...", foreground=TRANSLITERATION_COLOR))
            return
        
        if current_input_lang_code not in ('auto', 'en'):
            speech_text_transliteration = transliterate_text(speech_text, lang_code=current_input_lang_code)
        else:
            speech_text_transliteration = speech_text
            
        translated_text = GoogleTranslator(source=current_input_lang_code, target=language_codes.get(output_lang.get(), 'en')).translate(text=speech_text_transliteration)
        last_translated_text = translated_text
        
        with open("voice_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] Translated: {translated_text}\n")

        voice = gTTS(translated_text, lang=language_codes.get(output_lang.get(), 'en'))
        voice.save('voice.mp3')
        playsound('voice.mp3')
        os.remove('voice.mp3')

        win.after(0, lambda: output_text.config(state='normal'))
        win.after(0, lambda: output_text.insert(tk.END, f"[{timestamp}] Translated: {translated_text}\n"))
        win.after(0, lambda: output_text.see(tk.END))
        win.after(0, lambda: output_text.config(state='disabled'))
        
        win.after(0, lambda: play_offline_button.config(state='normal'))
        
        print("✅ Recognition and translation successful.")
        win.after(0, lambda: live_transliteration_label.config(text="Speak to see live transliteration...", foreground=TRANSLITERATION_COLOR))
        
    except sr.UnknownValueError:
        win.after(0, lambda: input_text.config(state='normal'))
        win.after(0, lambda: input_text.insert(tk.END, f"[{timestamp}] Input Error: Could not understand audio for final processing!\n", 'error'))
        win.after(0, lambda: input_text.see(tk.END))
        win.after(0, lambda: input_text.config(state='disabled'))
        win.after(0, lambda: output_text.config(state='normal'))
        win.after(0, lambda: output_text.insert(tk.END, f"[{timestamp}] Output Error: Could not understand!\n", 'error'))
        win.after(0, lambda: output_text.see(tk.END))
        win.after(0, lambda: output_text.config(state='disabled'))
        print("❌ Sorry, couldn't understand audio during final processing.")
        with open("voice_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] Error: Could not understand audio (final).\n")
        win.after(0, lambda: live_transliteration_label.config(text="Could not understand this phrase...", foreground=ERROR_COLOR))
    except sr.RequestError as e:
        win.after(0, lambda: input_text.config(state='normal'))
        win.after(0, lambda: input_text.insert(tk.END, f"[{timestamp}] Input Error: Could not request from Google (final): {e}\n", 'error'))
        win.after(0, lambda: input_text.see(tk.END))
        win.after(0, lambda: input_text.config(state='disabled'))
        win.after(0, lambda: output_text.config(state='normal'))
        win.after(0, lambda: output_text.insert(tk.END, f"[{timestamp}] Output Error: Could not request from Google (final): {e}\n", 'error'))
        win.after(0, lambda: output_text.see(tk.END))
        win.after(0, lambda: output_text.config(state='disabled'))
        print(f"❌ API request error during final processing: {e}")
        with open("voice_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] Error: API request error (final): {e}\n")
        win.after(0, lambda: live_transliteration_label.config(text=f"API Error (final): {e}", foreground=ERROR_COLOR))
    except Exception as e:
        print(f"An unexpected error occurred during final processing: {e}")
        win.after(0, lambda: live_transliteration_label.config(text=f"Error (final): {e}", foreground=ERROR_COLOR))
        win.after(0, lambda: input_text.config(state='normal'))
        win.after(0, lambda: input_text.insert(tk.END, f"[{timestamp}] Unexpected Error (final): {e}\n", 'error'))
        win.after(0, lambda: input_text.see(tk.END))
        win.after(0, lambda: input_text.config(state='disabled'))
        win.after(0, lambda: output_text.config(state='normal'))
        win.after(0, lambda: output_text.insert(tk.END, f"[{timestamp}] Unexpected Error (final): {e}\n", 'error'))
        win.after(0, lambda: output_text.see(tk.END))
        win.after(0, lambda: output_text.config(state='disabled'))


def run_translator():
    global keep_running
    if not keep_running:
        keep_running = True
        update_microphone_status("🟡 Starting...", INFO_COLOR)
        print("Starting translation loop...")
        threading.Thread(target=update_translation_loop).start()

def kill_execution():
    global keep_running
    keep_running = False
    print("Stopping translation loop...")
    update_microphone_status("🔴 Not Listening", ERROR_COLOR)
    win.after(0, lambda: live_transliteration_label.config(text="Speak to see live transliteration...", foreground=TRANSLITERATION_COLOR))
    win.after(0, lambda: play_offline_button.config(state='disabled'))


def trigger_immediate_processing():
    global immediate_process_flag
    if keep_running:
        immediate_process_flag.set()
        print("💡 Immediate processing triggered.")
    else:
        print("⚠️ Translator is not running. Start translation first.")


def play_offline_audio():
    global last_translated_text, tts_engine
    if tts_engine and last_translated_text:
        try:
            print(f"🔊 Playing offline: '{last_translated_text}'")
            tts_engine.say(last_translated_text)
            tts_engine.runAndWait()
            print("Offline playback complete.")
        except Exception as e:
            print(f"❌ Error playing offline audio: {e}")
            win.after(0, lambda: live_transliteration_label.config(text=f"Offline Playback Error: {e}", foreground=ERROR_COLOR))
    else:
        print("⚠️ No text translated yet or pyttsx3 engine not initialized.")
        win.after(0, lambda: live_transliteration_label.config(text="No text for offline playback or engine error.", foreground=INFO_COLOR))


def open_about_page():
    about_window = tk.Toplevel(win)
    about_window.title("About EchoWrite") # Updated title
    about_window.iconphoto(False, icon)
    about_window.geometry("500x350")
    about_window.transient(win)
    about_window.grab_set()
    about_window.configure(bg=PRIMARY_DARK)

    about_style = ttk.Style()
    about_style.configure('About.TLabel', font=MEDIUM_FONT, padding=5, background=PRIMARY_DARK, foreground=TEXT_COLOR)
    about_style.configure('About.TButton', font=MEDIUM_FONT, background=HIGHLIGHT_COLOR, foreground=TEXT_COLOR, borderwidth=0, relief="flat")
    about_style.map('About.TButton', background=[('active', HIGHLIGHT_COLOR)], foreground=[('active', TEXT_COLOR)])
    
    about_style.configure('About.ScrolledText', font=(FONT_FAMILY, 10), borderwidth=1, relief="solid",
                          background=ACCENT_LIGHT, foreground='#333',
                          selectbackground=HIGHLIGHT_COLOR, selectforeground=TEXT_COLOR)


    ttk.Label(about_window, text="EchoWrite: Real-Time Voice Translator", font=LARGE_FONT, foreground=TRANSLITERATION_COLOR, background=PRIMARY_DARK).pack(pady=10)
    
    github_link = ttk.Label(about_window, text="github.com/SamirPaulb/real-time-voice-translator", underline=True, foreground="blue", cursor="hand2", style='About.TLabel')
    github_link.bind("<Button-1>", lambda e: open_webpage("https://github.com/SamirPaulb/real-time-voice-translator"))
    github_link.pack(pady=5)

    about_text_content = """
    EchoWrite is a machine learning project that translates voice from one language to another in real time while preserving the tone and emotion of the speaker, and outputs the result in MP3 format. Choose input and output languages from the dropdown menu and start the translation!

    Features:
    - Real-time voice translation
    - Live transliteration display (best effort with free API)
    - Automatic noise adjustment
    - Timestamps for all recognition/translation
    - Saves spoken text to voice_log.txt
    - Manual 'Process Now' button for immediate translation
    - Offline Text-to-Speech playback of translated text!

    Developed by: Samir Paul
    Version: v2.0.1
    """
    about_text = scrolledtext.ScrolledText(about_window, height=11, width=55, wrap=tk.WORD, state='disabled', relief="flat", style='About.ScrolledText')
    about_text.insert("1.0", about_text_content.strip())
    about_text.pack(pady=10, padx=10, fill='both', expand=True)

    close_button = ttk.Button(about_window, text="Close", command=about_window.destroy, style='About.TButton')
    close_button.pack(pady=10)

    win.wait_window(about_window)

def open_webpage(url):
    import webbrowser
    webbrowser.open(url)

# Run the Tkinter event loop
win.mainloop()