import io
from openai import OpenAI
import streamlit as st
import ffmpeg
import tempfile

def transcribe_audio(audio_bytes):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "audio.wav"  # OpenAI requires a filename
    
    try:
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1"
        )
        return transcript.text
    except Exception as e:
        raise Exception(f"Error transcribing audio: {str(e)}")