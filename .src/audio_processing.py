import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import audio_recorder
import io

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def transcribe_audio(audio_bytes):
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.mp3"
        
        transcription_response = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1"
        )
        
        if hasattr(transcription_response, 'text'):
            return transcription_response.text.strip()
        else:
            return "Transcriptie mislukt: Geen tekst ontvangen van de API."
    
    except Exception as e:
        st.error(f"Fout bij het transcriberen: {str(e)}")
        return f"Transcriptie mislukt: {str(e)}"

def process_audio_input():
    st.write("Debug: process_audio_input function called")
    st.write("Klik op de microfoon om de opname te starten en te stoppen.")
    audio_bytes = audio_recorder(text="", recording_color="#e8b62c", neutral_color="#6aa36f")
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")
        if st.button("Transcribeer Audio"):
            with st.spinner("Transcriberen van audio..."):
                transcript = transcribe_audio(audio_bytes)
            return transcript
    
    return None

# Add this line at the end of the file
st.write("Debug: audio_processing.py loaded")