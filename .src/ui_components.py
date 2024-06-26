import streamlit as st
from st_audiorec import st_audiorec
import pyperclip

def display_recorder():
    audio_bytes = st_audiorec()
    return audio_bytes

def display_editable_transcript(transcript):
    return st.text_area("Bewerk transcript indien nodig", value=transcript, height=200)

def display_email_body(email_body):
    st.text_area("Gegenereerde E-mailtekst", value=email_body, height=300)
    if st.button("Kopieer naar Klembord"):
        pyperclip.copy(email_body)
        st.success("E-mailtekst gekopieerd naar klembord!")