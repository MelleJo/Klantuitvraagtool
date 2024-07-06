import streamlit as st
from utils.transcription import process_audio_input, display_logs
from utils.nlp import analyze_transcript
from utils.email import generate_email
from utils.attachment import generate_attachment
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize session state variables
if 'processing_complete' not in st.session_state:
    st.session_state['processing_complete'] = False
if 'transcription_done' not in st.session_state:
    st.session_state['transcription_done'] = False
if 'transcript' not in st.session_state:
    st.session_state['transcript'] = ""

def main():
    st.title("Klantuitvraagtool")

    # Input Section
    st.header("Input Section")
    input_method = st.radio("Kies de invoermethode", ["Upload audio", "Neem audio op"])

    try:
        logger.debug(f"Processing audio input with method: {input_method}")
        process_audio_input(input_method)
    except Exception as e:
        logger.error(f"Error in audio processing: {str(e)}", exc_info=True)
        st.error(f"An error occurred during audio processing: {str(e)}")

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

    # Display detailed logs
    st.header("Debug Information")
    display_logs()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Unhandled exception in main: {str(e)}", exc_info=True)
        st.error(f"An unexpected error occurred: {str(e)}")