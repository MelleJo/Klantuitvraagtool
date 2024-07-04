import streamlit as st
from openai import OpenAI
import io
from pydub import AudioSegment

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def convert_audio_to_wav(audio_bytes, original_format):
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=original_format)
        buf = io.BytesIO()
        audio.export(buf, format="wav")
        return buf.getvalue()
    except Exception as e:
        st.error(f"Fout bij het converteren van audio: {str(e)}")
        return None

def transcribe_audio(audio_bytes, file_format):
    try:
        # Convert audio to WAV format
        wav_audio = convert_audio_to_wav(audio_bytes, file_format)
        if wav_audio is None:
            return "Transcriptie mislukt: Kon het audiobestand niet converteren."

        audio_file = io.BytesIO(wav_audio)
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