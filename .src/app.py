import streamlit as st
from audio_processing import transcribe_audio
from email_generator import generate_email
from ui_components import display_recorder, display_transcript, display_email
from config import load_config
from openai_utils import client
import io

def main():
    st.set_page_config(page_title="Adviseur E-mail Generator", layout="wide")
    
    if not client:
        st.error("OpenAI client niet geïnitialiseerd. Controleer uw API-sleutel.")
        return

    config = load_config()
    
    st.title("Adviseur E-mail Generator")
    
    with st.sidebar:
        st.subheader("Audio Opname")
        audio_bytes = display_recorder()
        
        if audio_bytes is not None:
            # Convert audio_bytes to BytesIO object
            audio_file = io.BytesIO(audio_bytes)
            st.audio(audio_file)
            if st.button("Transcribeer Audio"):
                transcript = transcribe_audio(audio_bytes)
                st.session_state.transcript = transcript
                st.success("Audio getranscribeerd!")

        if st.button("Genereer E-mail"):
            if 'transcript' in st.session_state:
                email_content = generate_email(st.session_state.transcript, config['email_templates'])
                st.session_state.email = email_content
                st.success("E-mail gegenereerd!")
            else:
                st.warning("Transcribeer eerst de audio voordat u een e-mail genereert.")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Opgenomen Informatie")
        if 'transcript' in st.session_state:
            display_transcript(st.session_state.transcript)
    
    with col2:
        st.subheader("Gegenereerde E-mail")
        if 'email' in st.session_state:
            display_email(st.session_state.email)

if __name__ == "__main__":
    main()