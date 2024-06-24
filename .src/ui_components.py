import streamlit as st
from streamlit_mic_recorder import audio_recorder
import pyperclip

def display_recorder():
    audio_bytes = audio_recorder(
        text="Klik om de opname te starten/stoppen",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_name="microphone",
        icon_size="6x"
    )
    return audio_bytes

def display_transcript(transcript):
    st.text_area("Transcript", value=transcript, height=200)

def display_email(email_content):
    st.text_area("Gegenereerde E-mail", value=email_content, height=400)
    if st.button("Kopieer naar Klembord"):
        pyperclip.copy(email_content)
        st.success("E-mail gekopieerd naar klembord!")