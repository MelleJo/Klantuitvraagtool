import streamlit as st
from st_audiorec import st_audiorec
import pyperclip

def display_recorder():
    audio_bytes = st_audiorec()
    return audio_bytes

def display_transcript(transcript):
    edited_transcript = st.text_area("Transcript (bewerk indien nodig)", value=transcript, height=200)
    return edited_transcript

def display_email(email_content):
    st.text_area("Gegenereerde E-mailtekst", value=email_content, height=400)
    if st.button("Kopieer naar Klembord"):
        pyperclip.copy(email_content)
        st.success("E-mailtekst gekopieerd naar klembord!")