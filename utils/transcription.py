import streamlit as st
from pydub import AudioSegment
import tempfile
from utils.api_calls import get_openai_client
from streamlit_mic_recorder import mic_recorder
import os
import subprocess
import json
import shutil

def is_ffmpeg_available():
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def split_audio(file_path, max_duration_ms=30000):
    try:
        log(f"Trying to load audio file from: {file_path}")
        if not os.path.exists(file_path):
            log(f"Error: File not found at {file_path}")
            return None
        
        if is_ffmpeg_available():
            return split_audio_ffmpeg(file_path, max_duration_ms)
        else:
            log("FFmpeg not available. Falling back to pydub.")
            return split_audio_pydub(file_path, max_duration_ms)
    except Exception as e:
        log(f"Error in split_audio: {str(e)}")
        return None

def split_audio_ffmpeg(file_path, max_duration_ms):
    try:
        ffprobe_cmd = [
            'ffprobe', 
            '-v', 'quiet', 
            '-print_format', 'json', 
            '-show_format', 
            '-show_streams', 
            file_path
        ]
        
        ffprobe_output = subprocess.check_output(ffprobe_cmd, stderr=subprocess.STDOUT).decode('utf-8')
        ffprobe_data = json.loads(ffprobe_output)
        
        duration = float(ffprobe_data['format']['duration']) * 1000  # Convert to milliseconds
        
        chunks = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for i in range(0, int(duration), max_duration_ms):
                output_file = os.path.join(temp_dir, f"chunk_{i}.wav")
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-i', file_path,
                    '-ss', str(i / 1000),
                    '-t', str(max_duration_ms / 1000),
                    '-acodec', 'pcm_s16le',
                    '-ar', '16000',
                    '-ac', '1',
                    '-y',
                    output_file
                ]
                try:
                    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    chunks.append(output_file)
                except subprocess.CalledProcessError as e:
                    log(f"Error processing chunk {i}: {e.stderr.decode('utf-8')}")
                    continue
            
            if not chunks:
                log("No chunks were successfully created.")
                return None
            
            # Copy chunks to a more persistent location
            persistent_chunks = []
            for i, chunk in enumerate(chunks):
                persistent_path = f"/tmp/persistent_chunk_{i}.wav"
                shutil.copy2(chunk, persistent_path)
                persistent_chunks.append(persistent_path)
        
        log(f"Audio successfully split into {len(persistent_chunks)} chunks using FFmpeg.")
        return persistent_chunks
    except subprocess.CalledProcessError as e:
        log(f"Error running ffmpeg or ffprobe: {e.stderr.decode('utf-8')}")
        return None
    except Exception as e:
        log(f"Unexpected error in split_audio_ffmpeg: {str(e)}")
        return None

def split_audio_pydub(file_path, max_duration_ms):
    try:
        audio = AudioSegment.from_file(file_path)
        chunks = []
        for i, chunk in enumerate(audio[::max_duration_ms]):
            output_file = f"/tmp/chunk_{i}.wav"
            chunk.export(output_file, format="wav")
            chunks.append(output_file)
        log(f"Audio successfully split into {len(chunks)} chunks using pydub.")
        return chunks
    except Exception as e:
        log(f"Error splitting audio with pydub: {str(e)}")
        return None

def transcribe_audio(file_path):
    transcript_text = ""
    try:
        audio_segments = split_audio(file_path)
        if audio_segments is None or len(audio_segments) == 0:
            return "Audio segmentation failed."
    except Exception as e:
        log(f"Error during audio segmentation: {str(e)}")
        return "Audio segmentation failed."

    total_segments = len(audio_segments)
    progress_bar = st.progress(0)
    progress_text = st.empty()
    progress_text.text("Starting transcription...")
    for i, segment_file in enumerate(audio_segments):
        progress_text.text(f'Processing segment {i+1} of {total_segments} - {((i+1)/total_segments*100):.2f}% completed')
        try:
            if not os.path.exists(segment_file):
                log(f"Segment file not found: {segment_file}")
                continue
            
            with open(segment_file, "rb") as audio_file:
                client = get_openai_client()
                transcription_response = client.audio.transcriptions.create(file=audio_file, model="whisper-1")
                if hasattr(transcription_response, 'text'):
                    transcript_text += transcription_response.text + " "
                    log(f"Segment {i+1} transcription: {transcription_response.text}")
                else:
                    log(f"Unexpected response format for segment {i+1}")
        except Exception as e:
            log(f"Error during transcription of segment {i+1}: {str(e)}")
            continue
        finally:
            try:
                os.remove(segment_file)
            except Exception as e:
                log(f"Error removing temporary file {segment_file}: {str(e)}")
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
                        log(f"Error processing uploaded audio file: {str(e)}")
                        st.error("An error occurred while processing the audio file.")
                    finally:
                        try:
                            os.unlink(tmp_audio.name)
                        except Exception as e:
                            log(f"Error removing temporary file: {str(e)}")
                st.session_state['transcription_done'] = True
                st.experimental_rerun()
        elif input_method == "Neem audio op":
            audio_data = mic_recorder(key="recorder", start_prompt="Start opname", stop_prompt="Stop opname", use_container_width=True, format="webm")
            if audio_data and 'bytes' in audio_data and not st.session_state.get('transcription_done', False):
                with st.spinner("Transcribing audio..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_audio:
                            tmp_audio.write(audio_data['bytes'])
                            tmp_audio.flush()
                            log(f"Recorded audio saved to temporary file: {tmp_audio.name}")
                            st.session_state['transcript'] = transcribe_audio(tmp_audio.name)
                    except Exception as e:
                        log(f"Error processing recorded audio file: {str(e)}")
                        st.error("An error occurred while processing the recorded audio.")
                    finally:
                        try:
                            os.unlink(tmp_audio.name)
                        except Exception as e:
                            log(f"Error removing temporary file: {str(e)}")
                st.session_state['transcription_done'] = True
                st.experimental_rerun()

def log(message):
    if 'log_details' not in st.session_state:
        st.session_state['log_details'] = ""
    st.session_state['log_details'] += f"{message}\n"

def display_logs():
    if 'log_details' in st.session_state:
        st.text_area("Detailed Logs", st.session_state['log_details'], height=300)