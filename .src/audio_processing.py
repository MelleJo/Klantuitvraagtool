import streamlit as st
from pydub import AudioSegment
import tempfile
from openai_service import get_openai_client
from streamlit_mic_recorder import mic_recorder
import io

def split_audio(file_path, max_duration_ms=30000):
    audio = AudioSegment.from_file(file_path)
    chunks = []
    for i in range(0, len(audio), max_duration_ms):
        chunks.append(audio[i:i+max_duration_ms])
    return chunks

def transcribe_audio(file_path):
    transcript_text = ""
    with st.spinner('Audio segmentatie wordt gestart...'):
        try:
            audio_segments = split_audio(file_path)
        except Exception as e:
            st.error(f"Fout bij het segmenteren van het audio: {str(e)}")
            return "Segmentatie mislukt."

    total_segments = len(audio_segments)
    progress_bar = st.progress(0)
    progress_text = st.empty()
    progress_text.text("Start transcriptie...")
    for i, segment in enumerate(audio_segments):
        progress_text.text(f'Bezig met verwerken van segment {i+1} van {total_segments} - {((i+1)/total_segments*100):.2f}% voltooid')
        with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as temp_file:
            segment.export(temp_file.name, format="wav")
            with open(temp_file.name, "rb") as audio_file:
                try:
                    client = get_openai_client()
                    transcription_response = client.audio.transcriptions.create(file=audio_file, model="whisper-1")
                    if hasattr(transcription_response, 'text'):
                        transcript_text += transcription_response.text + " "
                except Exception as e:
                    st.error(f"Fout bij het transcriberen: {str(e)}")
                    continue
        progress_bar.progress((i + 1) / total_segments)
    progress_text.success("Transcriptie voltooid.")
    return transcript_text.strip()

def record_audio():
    st.write("Debug: Entering record_audio function")
    try:
        st.write("Klik op de microfoon om de opname te starten en te stoppen.")
        audio_data = mic_recorder(key="recorder", start_prompt="Start opname", stop_prompt="Stop opname", use_container_width=True)
        st.write(f"Debug: mic_recorder returned {type(audio_data)}")
        return audio_data
    except Exception as e:
        st.error(f"Error in record_audio: {str(e)}")
        return None

def upload_audio():
    st.write("Debug: Entering upload_audio function")
    try:
        uploaded_file = st.file_uploader("Upload een audiobestand", type=['wav', 'mp3', 'mp4', 'm4a', 'ogg', 'webm'])
        st.write(f"Debug: file_uploader returned {type(uploaded_file)}")
        return uploaded_file
    except Exception as e:
        st.error(f"Error in upload_audio: {str(e)}")
        return None

# Debug: Print when this module is imported
st.write("Debug: audio_processing.py has been imported")