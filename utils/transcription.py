import streamlit as st
from pydub import AudioSegment
import tempfile
from utils.api_calls import get_openai_client
from streamlit_mic_recorder import mic_recorder

import subprocess
import json

def split_audio(file_path, max_duration_ms=30000):
    try:
        log(f"Trying to load audio file from: {file_path}")
        
        # Get audio duration using ffprobe
        ffprobe_cmd = [
            'ffprobe', 
            '-v', 'quiet', 
            '-print_format', 'json', 
            '-show_format', 
            '-show_streams', 
            file_path
        ]
        
        ffprobe_output = subprocess.check_output(ffprobe_cmd).decode('utf-8')
        ffprobe_data = json.loads(ffprobe_output)
        
        duration = float(ffprobe_data['format']['duration']) * 1000  # Convert to milliseconds
        
        chunks = []
        for i in range(0, int(duration), max_duration_ms):
            output_file = f"/tmp/chunk_{i}.wav"
            ffmpeg_cmd = [
                'ffmpeg',
                '-i', file_path,
                '-ss', str(i / 1000),
                '-t', str(max_duration_ms / 1000),
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                output_file
            ]
            subprocess.run(ffmpeg_cmd, check=True)
            chunks.append(output_file)
        
        log(f"Audio successfully split into {len(chunks)} chunks.")
        return chunks
    except subprocess.CalledProcessError as e:
        log(f"Error running ffmpeg or ffprobe: {str(e)}")
        return None
    except Exception as e:
        log(f"Error loading or splitting audio file: {str(e)}")
        return None

def transcribe_audio(file_path):
    transcript_text = ""
    try:
        audio_segments = split_audio(file_path)
        if audio_segments is None:
            return "Segmentation failed."
    except Exception as e:
        log(f"Error during audio segmentation: {str(e)}")
        return "Segmentation failed."

    total_segments = len(audio_segments)
    progress_bar = st.progress(0)
    progress_text = st.empty()
    progress_text.text("Starting transcription...")
    for i, segment_file in enumerate(audio_segments):
        progress_text.text(f'Processing segment {i+1} of {total_segments} - {((i+1)/total_segments*100):.2f}% completed')
        try:
            with open(segment_file, "rb") as audio_file:
                client = get_openai_client()
                transcription_response = client.audio.transcriptions.create(file=audio_file, model="whisper-1")
                if hasattr(transcription_response, 'text'):
                    transcript_text += transcription_response.text + " "
                    log(f"Segment {i+1} transcription: {transcription_response.text}")
        except Exception as e:
            log(f"Error during transcription: {str(e)}")
            continue
        finally:
            # Clean up the temporary file
            subprocess.run(['rm', segment_file], check=True)
        progress_bar.progress((i + 1) / total_segments)
    progress_text.success("Transcription completed.")
    return transcript_text.strip()

def process_audio_input(input_method):
    if not st.session_state.get('processing_complete', False):
        if input_method == "Upload audio":
            uploaded_file = st.file_uploader("Upload an audio file", type=['wav', 'mp3', 'mp4', 'm4a', 'ogg', 'webm'])
            if uploaded_file is not None and not st.session_state.get('transcription_done', False):
                with st.spinner("Transcribing audio..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                            tmp_audio.write(uploaded_file.getvalue())
                            tmp_audio.flush()
                            log(f"Uploaded audio file saved to temporary file: {tmp_audio.name}")
                        st.session_state['transcript'] = transcribe_audio(tmp_audio.name)
                    except Exception as e:
                        log(f"Error processing audio file: {str(e)}")
                    finally:
                        tempfile.NamedTemporaryFile(delete=True)
                st.session_state['transcription_done'] = True
                st.experimental_rerun()
        elif input_method == "Neem audio op":
            audio_data = mic_recorder(key="recorder", start_prompt="Start opname", stop_prompt="Stop opname", use_container_width=True, format="webm")
            if audio_data and 'bytes' in audio_data and not st.session_state.get('transcription_done', False):
                with st.spinner("Transcribing audio..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                            tmp_audio.write(audio_data['bytes'])
                            tmp_audio.flush()
                            log(f"Recorded audio saved to temporary file: {tmp_audio.name}")
                        st.session_state['transcript'] = transcribe_audio(tmp_audio.name)
                    except Exception as e:
                        log(f"Error processing audio file: {str(e)}")
                    finally:
                        tempfile.NamedTemporaryFile(delete=True)
                st.session_state['transcription_done'] = True
                st.experimental_rerun()

def log(message):
    if 'log_details' not in st.session_state:
        st.session_state['log_details'] = ""
    st.session_state['log_details'] += f"{message}\n"

def display_logs():
    if 'log_details' in st.session_state:
        st.text_area("Detailed Logs", st.session_state['log_details'], height=300)
