import streamlit as st
from audio_processing import transcribe_audio
from email_generator import generate_email
from ui_components import display_recorder, display_transcript, display_email
from config import load_config
from openai_utils import client

def main():
    st.set_page_config(page_title="Advisor Email Generator", layout="wide")
    
    if not client:
        st.error("OpenAI client not initialized. Please check your API key.")
        return
    
    config = load_config()
    
    st.title("Advisor Email Generator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Record Client Information")
        audio_data = display_recorder()
        
        if audio_data:
            transcript = transcribe_audio(audio_data)
            display_transcript(transcript)
    
    with col2:
        st.subheader("Generated Email")
        if 'transcript' in locals():
            email_content = generate_email(transcript, config['email_templates'])
            display_email(email_content)

if __name__ == "__main__":
    main()