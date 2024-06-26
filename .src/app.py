import streamlit as st
from audio_processing import transcribe_audio
from email_generator import generate_email_body
from ui_components import display_recorder, display_editable_transcript, display_email_body
import io

def main():
    st.set_page_config(page_title="Adviseur E-mail Generator", layout="wide")
    
    # Load external CSS
    with open('styles/main.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    api_key = st.secrets["OPENAI_API_KEY"]
    if not api_key:
        st.error("OpenAI API-sleutel niet gevonden. Controleer uw Streamlit Secrets.")
        return

    st.title("Adviseur E-mail Generator")
    
    with st.sidebar:
        st.subheader("Audio Opname")
        audio_bytes = display_recorder()
        
        if audio_bytes is not None:
            if st.button("Transcribeer Audio"):
                try:
                    transcript = transcribe_audio(audio_bytes)
                    st.session_state.transcript = transcript
                    st.success("Audio getranscribeerd!")
                except Exception as e:
                    st.error(f"Fout bij het transcriberen van audio: {str(e)}")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Opgenomen Informatie")
        if 'transcript' in st.session_state:
            edited_transcript = display_editable_transcript(st.session_state.transcript)
            if edited_transcript != st.session_state.transcript:
                st.session_state.transcript = edited_transcript
                st.success("Transcript bijgewerkt!")

        if st.button("Bevestig Transcript"):
            if 'transcript' in st.session_state:
                try:
                    email_body = generate_email_body(st.session_state.transcript, api_key)
                    st.session_state.email_body = email_body
                    st.success("E-mailtekst gegenereerd!")
                except Exception as e:
                    st.error(f"Er is een fout opgetreden bij het genereren van de e-mailtekst: {str(e)}")

    with col2:
        st.subheader("Gegenereerde E-mailtekst")
        if 'email_body' in st.session_state:
            display_email_body(st.session_state.email_body)

if __name__ == "__main__":
    main()