import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import pyperclip
from pydub import AudioSegment
import io

def display_recorder():
    webrtc_ctx = webrtc_streamer(
        key="audio-recorder",
        mode=WebRtcMode.AUDIO_RECORDER,
        audio_recorder_config={"sample_rate": 16000},
    )
    
    if webrtc_ctx.audio_recorder_state.recording:
        st.write("Recording... (Click stop to finish)")
    elif webrtc_ctx.audio_recorder_state.recorded:
        st.audio(webrtc_ctx.audio_recorder_state.recorded_audio, format="audio/wav")
        audio_bytes = webrtc_ctx.audio_recorder_state.audio_data
        return audio_bytes
    return None

def display_editable_transcript(transcript):
    return st.text_area("Bewerk transcript indien nodig", value=transcript, height=200)

def display_email_body(email_body):
    st.text_area("Gegenereerde E-mailtekst", value=email_body, height=300)
    if st.button("Kopieer naar Klembord"):
        pyperclip.copy(email_body)
        st.success("E-mailtekst gekopieerd naar klembord!")