import logging
import tempfile
from pydub import AudioSegment
from openai import OpenAI
import streamlit as st
from streamlit_mic_recorder import mic_recorder
import json
import uuid

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def split_audio(file_path, max_duration_ms=30000):
    audio = AudioSegment.from_file(file_path)
    chunks = []
    for i in range(0, len(audio), max_duration_ms):
        chunks.append(audio[i:i+max_duration_ms])
    return chunks

def transcribe_audio(file_path):
    logger.debug(f"Starting transcribe_audio for file: {file_path}")
    transcript_text = ""
    with st.spinner('Audio segmentatie wordt gestart...'):
        try:
            audio_segments = split_audio(file_path)
            logger.debug(f"Audio split into {len(audio_segments)} segments")
        except Exception as e:
            logger.error(f"Error splitting audio: {str(e)}")
            st.error(f"Fout bij het segmenteren van het audio: {str(e)}")
            return "Segmentatie mislukt."

    total_segments = len(audio_segments)
    progress_bar = st.progress(0)
    progress_text = st.empty()
    progress_text.text("Start transcriptie...")
    for i, segment in enumerate(audio_segments):
        logger.debug(f"Processing segment {i+1} of {total_segments}")
        progress_text.text(f'Bezig met verwerken van segment {i+1} van {total_segments} - {((i+1)/total_segments*100):.2f}% voltooid')
        with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as temp_file:
            segment.export(temp_file.name, format="wav")
            logger.debug(f"Segment exported to temporary file: {temp_file.name}")
            with open(temp_file.name, "rb") as audio_file:
                try:
                    transcription_response = client.audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-1",
                        response_format="text"
                    )
                    logger.debug(f"Transcription response received for segment {i+1}")
                    response_content = transcription_response.get('text', '') if isinstance(transcription_response, dict) else transcription_response
                    logger.debug(f"Transcription response content: {response_content}")
                    
                    transcript_text += response_content + " "
                except json.decoder.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON response for segment {i+1}: {e}")
                    response_content = transcription_response.content if hasattr(transcription_response, 'content') else "No content available"
                    logger.error(f"Response content for segment {i+1}: {response_content}")
                    st.error(f"Fout bij het transcriberen van segment {i+1}: {str(e)}")
                except Exception as e:
                    logger.error(f"Error transcribing segment {i+1}: {str(e)}")
                    st.error(f"Fout bij het transcriberen van segment {i+1}: {str(e)}")
        progress_bar.progress((i + 1) / total_segments)
    progress_text.success("Transcriptie voltooid.")
    logger.debug(f"Transcription completed. Total length: {len(transcript_text)}")
    st.info(f"Transcript gegenereerd. Lengte: {len(transcript_text)}")
    
    unique_key = f"generated_transcript_{uuid.uuid4()}"
    st.text_area("Gegenereerd Transcript", value=transcript_text, height=300, key=unique_key)
    
    return transcript_text.strip()

def process_audio_input(input_method):
    if input_method == "Upload audio":
        uploaded_file = st.file_uploader("Upload een audiobestand", type=['wav', 'mp3', 'mp4', 'm4a', 'ogg', 'webm'])
        if uploaded_file is not None:
            with st.spinner("Transcriberen van audio..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                    tmp_audio.write(uploaded_file.getvalue())
                    tmp_audio.flush()
                    transcript = transcribe_audio(tmp_audio.name)
                tempfile.NamedTemporaryFile(delete=True)
            st.session_state['transcript'] = transcript
            st.session_state['input_processed'] = True
            return tmp_audio.name  # Return the file path instead of the transcript
    elif input_method == "Neem audio op":
        audio_data = mic_recorder(key="recorder", start_prompt="Start opname", stop_prompt="Stop opname", use_container_width=True)
        if audio_data and 'bytes' in audio_data:
            with st.spinner("Transcriberen van audio..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                    tmp_audio.write(audio_data['bytes'])
                    tmp_audio.flush()
                    transcript = transcribe_audio(tmp_audio.name)
                tempfile.NamedTemporaryFile(delete=True)
            st.session_state['transcript'] = transcript
            st.session_state['input_processed'] = True
            return tmp_audio.name  # Return the file path instead of the transcript
    return None

print("audio_processing.py loaded successfully")
