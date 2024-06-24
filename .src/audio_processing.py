import tempfile
from openai_utils import client

def transcribe_audio(audio_data):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_data)
        temp_audio.flush()
        
        with open(temp_audio.name, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                file=audio_file, 
                model="whisper-1"
            )
    
    return transcript.text