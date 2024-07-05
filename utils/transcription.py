import streamlit as st
from pydub import AudioSegment
import tempfile
from utils.api_calls import get_openai_client
from streamlit_mic_recorder import mic_recorder

def split_audio(file_path, max_duration_ms=30000):
    try:
        st.write(f"Trying to load audio file from: {file_path}")
        audio = AudioSegment.from_file(file_path)
        chunks = []
        for i in range(0, len(audio), max_duration_ms):
            chunks.append(audio[i:i+max_duration_ms])
        st.write(f"Audio successfully split into {len(chunks)} chunks.")
        return chunks
    except Exception as e:
        st.error(f"Error loading or splitting audio file: {str(e)}")
        return None

def transcribe_audio(file_path):
    transcript_text = ""
    with st.spinner('Audio segmentation started...'):
        try:
            audio_segments = split_audio(file_path)
            if audio_segments is None:
                return "Segmentation failed."
        except Exception as e:
            st.error(f"Error during audio segmentation: {str(e)}")
            return "Segmentation failed."

    total_segments = len(audio_segments)
    progress_bar = st.progress(0)
    progress_text = st.empty()
    progress_text.text("Starting transcription...")
    for i, segment in enumerate(audio_segments):
        progress_text.text(f'Processing segment {i+1} of {total_segments} - {((i+1)/total_segments*100):.2f}% completed')
        with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as temp_file:
            segment.export(temp_file.name, format="wav")
            st.write(f"Segment {i+1} exported to temporary file.")
            with open(temp_file.name, "rb") as audio_file:
                try:
                    client = get_openai_client()
                    transcription_response = client.audio.transcriptions.create(file=audio_file, model="whisper-1")
                    if hasattr(transcription_response, 'text'):
                        transcript_text += transcription_response.text + " "
                        st.write(f"Segment {i+1} transcription: {transcription_response.text}")
                except Exception as e:
                    st.error(f"Error during transcription: {str(e)}")
                    continue
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
                            st.write(f"Uploaded audio file saved to temporary file: {tmp_audio.name}")
                        st.session_state['transcript'] = transcribe_audio(tmp_audio.name)
                    except Exception as e:
                        st.error(f"Error processing audio file: {str(e)}")
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
                            st.write(f"Recorded audio saved to temporary file: {tmp_audio.name}")
                        st.session_state['transcript'] = transcribe_audio(tmp_audio.name)
                    except Exception as e:
                        st.error(f"Error processing audio file: {str(e)}")
                    finally:
                        tempfile.NamedTemporaryFile(delete=True)
                st.session_state['transcription_done'] = True
                st.experimental_rerun()
