import streamlit as st
import io
import tempfile
import os
from openai_service import get_openai_client
from streamlit_mic_recorder import mic_recorder
from services.summarization_service import summarize_text
from utils.text_processing import update_gesprekslog

def process_audio(audio_file, chunk_size_mb=10):
    chunk_size = chunk_size_mb * 1024 * 1024  # Convert MB to bytes
    chunks = []
    
    while True:
        chunk = audio_file.read(chunk_size)
        if not chunk:
            break
        chunks.append(chunk)
    
    return chunks

def transcribe_audio(file_path):
    transcript_text = ""
    with st.spinner('Processing audio...'):
        with open(file_path, 'rb') as audio_file:
            audio_chunks = process_audio(audio_file)

    total_chunks = len(audio_chunks)
    progress_bar = st.progress(0)
    progress_text = st.empty()
    progress_text.text("Starting transcription...")
    
    for i, chunk in enumerate(audio_chunks):
        progress_text.text(f'Processing chunk {i+1} of {total_chunks} - {((i+1)/total_chunks*100):.2f}% complete')
        try:
            client = get_openai_client()
            with io.BytesIO(chunk) as audio_chunk:
                transcription_response = client.audio.transcriptions.create(file=audio_chunk, model="whisper-1")
                if hasattr(transcription_response, 'text'):
                    transcript_text += transcription_response.text + " "
                else:
                    st.warning(f"Unexpected response format for chunk {i+1}")
        except Exception as e:
            st.error(f"Error transcribing chunk {i+1}: {str(e)}")
        progress_bar.progress((i + 1) / total_chunks)
    
    progress_text.success("Transcription completed.")
    return transcript_text.strip()

def process_audio_input(input_method):
    if not st.session_state.get('processing_complete', False):
        if input_method == "Upload audio":
            uploaded_file = st.file_uploader("Upload an audio file", type=['wav', 'mp3', 'mp4', 'm4a', 'ogg', 'webm'])
            if uploaded_file is not None and not st.session_state.get('transcription_done', False):
                with st.spinner("Transcribing audio..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix="." + uploaded_file.name.split('.')[-1]) as tmp_audio:
                        tmp_audio.write(uploaded_file.getvalue())
                        tmp_audio.flush()
                        st.session_state['transcript'] = transcribe_audio(tmp_audio.name)
                    os.unlink(tmp_audio.name)
                st.session_state['transcription_done'] = True
                st.experimental_rerun()
        elif input_method == "Neem audio op":
            audio_data = mic_recorder(key="recorder", start_prompt="Start recording", stop_prompt="Stop recording", use_container_width=True, format="webm")
            if audio_data and 'bytes' in audio_data and not st.session_state.get('transcription_done', False):
                with st.spinner("Transcribing audio..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_audio:
                        tmp_audio.write(audio_data['bytes'])
                        tmp_audio.flush()
                        st.session_state['transcript'] = transcribe_audio(tmp_audio.name)
                    os.unlink(tmp_audio.name)
                st.session_state['transcription_done'] = True
                st.experimental_rerun()
        
        if st.session_state.get('transcription_done', False) and not st.session_state.get('summarization_done', False):
            with st.spinner("Generating summary..."):
                st.session_state['summary'] = summarize_text(st.session_state['transcript'], st.session_state['department'])
            update_gesprekslog(st.session_state['transcript'], st.session_state['summary'])
            st.session_state['summarization_done'] = True
            st.session_state['processing_complete'] = True
            st.experimental_rerun()