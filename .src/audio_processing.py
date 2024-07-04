import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import io

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def transcribe_audio(audio_bytes):
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        
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
    audio_data = mic_recorder(key="recorder", start_prompt="Start opname", stop_prompt="Stop opname", use_container_width=True)
    
    if audio_data and isinstance(audio_data, dict) and 'bytes' in audio_data:
        audio_bytes = audio_data['bytes']
        try:
            st.audio(audio_bytes, format="audio/wav")
        except Exception as e:
            st.error(f"Fout bij het afspelen van audio: {str(e)}")
        
        if st.button("Transcribeer Audio"):
            with st.spinner("Transcriberen van audio..."):
                transcript = transcribe_audio(audio_bytes)
            return transcript
    
    return None