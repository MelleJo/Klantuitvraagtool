import streamlit as st
from streamlit_mic_recorder import mic_recorder
import pyperclip

def display_recorder():
    return mic_recorder(start_prompt="Start Opname", stop_prompt="Stop Opname", key='recorder')

def display_transcript(transcript):
    st.text_area("Transcript", value=transcript, height=200)

def display_email(email_content):
    st.text_area("Gegenereerde E-mail", value=email_content, height=400)
    if st.button("Kopieer naar Klembord"):
        pyperclip.copy(email_content)
        st.success("E-mail gekopieerd naar klembord!")