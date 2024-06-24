import streamlit as st
from audio_processing import transcribe_audio
from email_generator import generate_email
from ui_components import display_recorder, display_transcript, display_email
from config import load_config
from openai_utils import client
import io

def main():
    st.set_page_config(page_title="Adviseur E-mail Generator", layout="wide")
    
    # Custom CSS
    st.markdown("""
    <style>
        body {
            color: #333;
            font-family: 'Roboto', sans-serif;
        }
        .stApp {
            background-color: #f5f5f5;
        }
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3 {
            color: #003366;
        }
        .stButton>button {
            background-color: #008080;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #006666;
        }
        .card {
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 1rem;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)



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
        elif audio_data is not None:
            st.error("Onverwacht audio formaat. Neem opnieuw op.")

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