import streamlit as st
from pydub import AudioSegment
import tempfile
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder, audio_recorder
import io

def transcribe_audio(audio_bytes):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    with st.spinner('Audio transcriptie wordt uitgevoerd...'):
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
    st.write("Klik op de microfoon om de opname te starten en te stoppen.")
    audio_bytes = audio_recorder(text="", recording_color="#e8b62c", neutral_color="#6aa36f")
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")
        if st.button("Transcribeer Audio"):
            transcript = transcribe_audio(audio_bytes)
            return transcript
    
    return None