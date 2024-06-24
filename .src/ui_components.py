import streamlit as st
from streamlit_mic_recorder import mic_recorder
import pyperclip

def display_recorder():
    return mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", key='recorder')

def display_transcript(transcript):
    st.text_area("Transcript", value=transcript, height=200)

def display_email(email_content):
    st.text_area("Generated Email", value=email_content, height=400)
    if st.button("Copy to Clipboard"):
        pyperclip.copy(email_content)
        st.success("Email copied to clipboard!")