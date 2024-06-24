import streamlit as st
from audio_processing import transcribe_audio
from email_generator import generate_email
from ui_components import display_recorder, display_transcript, display_email
from config import load_config
from openai_utils import client

def main():
    st.set_page_config(page_title="Adviseur E-mail Generator", layout="wide")
    
    if not client:
        st.error("OpenAI client niet geïnitialiseerd. Controleer uw API-sleutel.")
        return

    config = load_config()
    
    st.title("Adviseur E-mail Generator")
    
    with st.sidebar:
        st.subheader("Opname Bediening")
        audio_data = display_recorder()
        
        if st.button("Genereer E-mail"):
            if 'transcript' in st.session_state:
                email_content = generate_email(st.session_state.transcript, config['email_templates'])
                st.session_state.email = email_content

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Opgenomen Informatie")
        if audio_data:
            transcript = transcribe_audio(audio_data)
            st.session_state.transcript = transcript
            display_transcript(transcript)
    
    with col2:
        st.subheader("Gegenereerde E-mail")
        if 'email' in st.session_state:
            display_email(st.session_state.email)

if __name__ == "__main__":
    main()