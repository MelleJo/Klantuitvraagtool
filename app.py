import streamlit as st
from utils.transcription import transcribe_audio, transcribe_text, whisper_stt
from utils.nlp import analyze_transcript
from utils.email import generate_email
from utils.attachment import generate_attachment

# Streamlit UI Layout
st.title("Klantuitvraagtool")

# Input Section
st.header("Input Section")
audio_file = st.file_uploader("Upload Audio File", type=["mp3", "wav", "mp4", "mpeg", "mpga", "m4a", "webm"])
text_input = st.text_area("Type or Paste Text")

if audio_file:
    transcript = transcribe_audio(audio_file)
    st.session_state['transcript'] = transcript
    st.text_area("Transcription", transcript)

if text_input:
    transcript = transcribe_text(text_input)
    st.session_state['transcript'] = transcript

st.write("Record your voice:")
recorded_text = whisper_stt(
    start_prompt="Start recording",
    stop_prompt="Stop recording",
    just_once=True,
    use_container_width=True,
    language="nl",
    key='recorder'
)
if recorded_text:
    st.session_state['transcript'] = recorded_text
    st.text_area("Transcription", recorded_text)

# Review Section
st.header("Review Section")
transcript = st.session_state.get('transcript', '')
if transcript:
    st.text_area("Transcription", transcript)
    analysis = analyze_transcript(transcript)
    st.session_state['analysis'] = analysis

# Email Generation Section
st.header("Email Generation Section")
if st.button("Generate Email"):
    email_content = generate_email(transcript, analysis)
    st.text_area("Generated Email", email_content)

# Attachment Generation Section
st.header("Attachment Generation Section")
if st.button("Generate Attachment"):
    attachment_content = generate_attachment(analysis)
    st.download_button("Download Attachment", attachment_content, file_name="attachment.pdf")
