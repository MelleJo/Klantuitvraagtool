import streamlit as st
from st_audiorec import st_audiorec
import pyperclip

def display_recorder():
    audio_bytes = st_audiorec()
    if audio_bytes is not None:
        st.write(f"Audio recorded. Type: {type(audio_bytes)}")
    return audio_bytes

def display_transcript(transcript):
    st.text_area("Transcript", value=transcript, height=200)

def display_email(email_content):
    st.text_area("Gegenereerde E-mail", value=email_content, height=400)
    if st.button("Kopieer naar Klembord"):
        pyperclip.copy(email_content)
        st.success("E-mail gekopieerd naar klembord!")