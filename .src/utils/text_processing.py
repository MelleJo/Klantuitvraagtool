import os
import pytz
from datetime import datetime
import streamlit as st
import pyperclip

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_prompt(file_name):
    project_root = get_project_root()
    path = os.path.join(project_root, 'prompts', file_name)
    print(f"Attempting to load prompt from: {path}")
    if not os.path.exists(path):
        st.error(f"Bestand niet gevonden: {path}")
        raise FileNotFoundError(f"Bestand niet gevonden: {path}")
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

def copy_to_clipboard(transcript, klantuitvraag):
    text_to_copy = f"Transcript:\n\n{transcript}\n\nKlantuitvraag:\n\n{klantuitvraag}"
    pyperclip.copy(text_to_copy)
    st.success("Transcript en klantuitvraag gekopieerd naar klembord!")

def get_local_time():
    timezone = pytz.timezone("Europe/Amsterdam")
    return datetime.now(timezone).strftime('%d-%m-%Y %H:%M:%S')

def update_gesprekslog(transcript, klantuitvraag):
    if 'gesprekslog' not in st.session_state:
        st.session_state.gesprekslog = []
    
    st.session_state.gesprekslog.append({
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'transcript': transcript,
        'klantuitvraag': klantuitvraag
    })
    
    # Keep only the last 5 conversations
    st.session_state.gesprekslog = st.session_state.gesprekslog[-5:]

print("text_processing.py loaded successfully")