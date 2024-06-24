import io
from openai_utils import client

def transcribe_audio(audio_bytes):
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "audio.wav"  # OpenAI vereist een bestandsnaam
    
    transcript = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-1"
    )
    
    return transcript.text