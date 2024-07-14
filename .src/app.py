import os
import streamlit as st
from utils.audio_processing import transcribe_audio, process_audio_input
from utils.file_processing import process_uploaded_file
from utils.text_processing import update_gesprekslog
from services.summarization_service import analyze_transcript, generate_email
from ui.components import (
    setup_page_style, display_transcript, display_klantuitvraag,
    display_input_method_selector, display_text_input, display_file_uploader,
    display_generate_button, display_progress_bar, display_spinner,
    display_success, display_error, display_warning
)
from ui.pages import render_feedback_form, render_conversation_history, render_suggestions

def load_config():
    return {
        "INPUT_METHODS": ["Voer tekst in of plak tekst", "Upload tekst", "Upload audio", "Neem audio op"],
    }

def initialize_session_state():
    if 'state' not in st.session_state:
        st.session_state.state = {
            'transcript': '',
            'edited_transcript': '',
            'klantuitvraag': '',
            'klantuitvraag_versions': [],
            'current_version_index': -1,
            'input_text': '',
            'gesprekslog': [],
            'product_info': '',
            'selected_products': [],
            'suggestions': [],
            'selected_suggestions': [],
            'email_content': '',
            'input_processed': False,
            'analysis_complete': False,
            'transcription_complete': False,
            'audio_file_path': None
        }

def main():
    setup_page_style()
    st.title("Klantuitvraagtool v0.0.2")
    st.markdown("---")

    config = load_config()
    initialize_session_state()
    
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("### 📋 Configuratie")
        input_method = display_input_method_selector(config["INPUT_METHODS"])

    with col2:
        st.markdown("### 📝 Transcript & Klantuitvraag")
        
        if not st.session_state.state['input_processed']:
            if input_method == "Upload tekst":
                uploaded_file = display_file_uploader(['txt', 'docx', 'pdf'])
                if uploaded_file:
                    transcript = process_uploaded_file(uploaded_file)
                    st.session_state.state['transcript'] = transcript
                    st.session_state.state['input_processed'] = True
                    st.session_state.state['transcription_complete'] = True

            elif input_method == "Voer tekst in of plak tekst":
                input_text = display_text_input()
                if display_generate_button():
                    transcript = input_text
                    st.session_state.state['transcript'] = transcript
                    st.session_state.state['input_processed'] = True
                    st.session_state.state['transcription_complete'] = True

            elif input_method in ["Upload audio", "Neem audio op"]:
                if not st.session_state.state['audio_file_path']:
                    st.session_state.state['audio_file_path'] = process_audio_input(input_method)
                audio_file_path = st.session_state.state['audio_file_path']
                if audio_file_path and not st.session_state.state['transcription_complete']:
                    with st.spinner("Audio wordt verwerkt en getranscribeerd..."):
                        transcript = transcribe_audio(audio_file_path)
                        st.session_state.state['transcript'] = transcript
                        st.session_state.state['input_processed'] = True
                        st.session_state.state['transcription_complete'] = True
                    os.unlink(audio_file_path)
                    st.session_state.state['audio_file_path'] = None
        
        transcript = st.session_state.state.get('transcript', '')
        if transcript:
            st.subheader("Transcript")
            st.text_area("Gegenereerd Transcript:", value=transcript, height=200, key="generated_transcript", disabled=True)

        st.subheader("Bewerk Transcript")
        edited_transcript = st.text_area(
            "Bewerk het transcript indien nodig:", 
            value=transcript, 
            height=300,
            key='transcript_editor'
        )
        st.session_state.state['edited_transcript'] = edited_transcript

        if st.button("Analyseer"):
            with st.spinner("Transcript analyseren..."):
                try:
                    st.session_state.state['suggestions'] = analyze_transcript(edited_transcript)
                    st.session_state.state['analysis_complete'] = True
                    display_success("Analyse voltooid!")
                except Exception as e:
                    display_error(f"Er is een fout opgetreden bij het analyseren van het transcript: {str(e)}")

        if st.session_state.state['analysis_complete']:
            st.session_state.state['selected_suggestions'] = render_suggestions(st.session_state.state['suggestions'])

            if st.button("Genereer E-mail"):
                with st.spinner("E-mail genereren..."):
                    try:
                        st.session_state.state['email_content'] = generate_email(
                            edited_transcript,
                            st.session_state.state['selected_suggestions']
                        )
                        st.session_state.state['klantuitvraag'] = st.session_state.state['email_content']
                        update_gesprekslog(edited_transcript, st.session_state.state['email_content'])
                        display_success("E-mail gegenereerd!")
                    except Exception as e:
                        display_error(f"Er is een fout opgetreden bij het genereren van de e-mail: {str(e)}")

        if st.session_state.state['klantuitvraag']:
            display_klantuitvraag(st.session_state.state['klantuitvraag'])

    st.markdown("---")
    render_conversation_history()
    
    with st.expander("Feedback", expanded=False):
        render_feedback_form()

if __name__ == "__main__":
    main()
