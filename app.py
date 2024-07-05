import streamlit as st
from utils.transcription import process_audio_input
from utils.nlp import analyze_transcript
from utils.email import generate_email
from utils.attachment import generate_attachment

# Initialize session state variables
if 'processing_complete' not in st.session_state:
    st.session_state['processing_complete'] = False
if 'transcription_done' not in st.session_state:
    st.session_state['transcription_done'] = False
if 'transcript' not in st.session_state:
    st.session_state['transcript'] = ""

st.title("Klantuitvraagtool")

# Input Section
st.header("Input Section")
input_method = st.radio("Kies de invoermethode", ["Upload audio", "Neem audio op"])

process_audio_input(input_method)

# Display transcription result
if st.session_state['transcription_done']:
    st.header("Transcriptie Resultaat")
    transcript = st.session_state['transcript']
    st.text_area("Transcriptie", transcript)

    # Analyze transcript
    if st.button("Analyseren Transcript"):
        analysis = analyze_transcript(transcript)
        st.session_state['analysis'] = analysis
        st.session_state['processing_complete'] = True

# Display analysis result
if st.session_state.get('processing_complete', False):
    st.header("Analyse Resultaat")
    analysis = st.session_state.get('analysis', '')
    st.text_area("Analyse", analysis)

    # Email Generation Section
    st.header("Email Generatie")
    if st.button("Genereer Email"):
        email_content = generate_email(transcript, analysis)
        st.text_area("Gegenereerde Email", email_content)

    # Attachment Generation Section
    st.header("Bijlage Generatie")
    if st.button("Genereer Bijlage"):
        attachment_content = generate_attachment(analysis)
        st.download_button("Download Bijlage", attachment_content, file_name="bijlage.pdf")
