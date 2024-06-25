import streamlit as st
from audio_processing import transcribe_audio
from email_generator import generate_email
from ui_components import display_recorder, display_transcript, display_email
from config import load_config
from openai_utils import client
import io

def main():
    st.set_page_config(page_title="Adviseur E-mail Generator", layout="wide")
    
    # Load external CSS
    with open('styles/main.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    if not client:
        st.error("OpenAI client niet geïnitialiseerd. Controleer uw API-sleutel.")
        return

    config = load_config()
    
    st.title("Adviseur E-mail Generator")
    
    with st.sidebar:
        st.subheader("Audio Opname")
        audio_data = display_recorder()
        
        if audio_data is not None and isinstance(audio_data, dict) and 'bytes' in audio_data:
            st.write(f"Audio opgenomen. Lengte: {len(audio_data['bytes'])} bytes")
            audio_bytes = audio_data['bytes']
            
            audio_file = io.BytesIO(audio_bytes)
            st.audio(audio_file)
            
            if st.button("Transcribeer Audio"):
                transcript = transcribe_audio(audio_bytes)
                st.session_state.transcript = transcript
                st.success("Audio getranscribeerd!")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Opgenomen Informatie")
        if 'transcript' in st.session_state:
            edited_transcript = display_transcript(st.session_state.transcript)
            if edited_transcript != st.session_state.transcript:
                st.session_state.transcript = edited_transcript
                st.success("Transcript bijgewerkt!")

    with col2:
        st.subheader("Gegenereerde E-mailtekst")
        if st.button("Genereer E-mailtekst"):
            if 'transcript' in st.session_state:
                email_content = generate_email(st.session_state.transcript, config['email_templates'])
                st.session_state.email = email_content
                st.success("E-mailtekst gegenereerd!")
                
                # Debug informatie
                st.write("Debug Informatie:")
                st.write(f"Taal detectie: {'Nederlands' if any(dutch_word in email_content.lower() for dutch_word in ['de', 'het', 'een', 'en', 'is']) else 'Niet Nederlands'}")
                st.write(f"Aantal karakters: {len(email_content)}")
                st.write(f"Eerste 100 karakters: {email_content[:100]}...")
                st.write(f"Laatste 100 karakters: ...{email_content[-100:]}")
                st.write(f"Bevat 'Subject:': {'Subject:' in email_content}")
                st.write(f"Bevat 'Dear': {'Dear' in email_content}")
                st.write(f"Bevat 'Best regards': {'Best regards' in email_content}")
        
        if 'email' in st.session_state:
            display_email(st.session_state.email)

if __name__ == "__main__":
    main()