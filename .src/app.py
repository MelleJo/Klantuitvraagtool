import os
import sys
import traceback
import importlib.util
import json
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

print("Starting app.py")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Content of current directory: {os.listdir('.')}")

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)
print(f"Updated sys.path: {sys.path}")

INPUT_METHODS = ["Voer tekst in of plak tekst", "Upload tekst", "Upload audio", "Neem audio op"]

def load_config():
    print("Loading configuration")
    return {
        "INPUT_METHODS": INPUT_METHODS,
    }

def load_product_descriptions():
    print("Loading product descriptions")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'product_descriptions.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading product descriptions: {str(e)}")
        return {}

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
        }
    print("Session state initialized:", st.session_state.state)

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
        print(f"DEBUG: Selected input method: {input_method}")

    with col2:
        st.markdown("### 📝 Transcript & Klantuitvraag")
        
        transcript = st.session_state.state.get('transcript', '')

        if input_method == "Upload tekst":
            uploaded_file = display_file_uploader(['txt', 'docx', 'pdf'])
            if uploaded_file:
                transcript = process_uploaded_file(uploaded_file)
                st.session_state.state['transcript'] = transcript
                st.session_state.state['input_processed'] = True
                print(f"DEBUG: Text file processed. Transcript: {transcript[:100]}")

        elif input_method == "Voer tekst in of plak tekst":
            input_text = display_text_input()
            if display_generate_button():
                transcript = input_text
                st.session_state.state['transcript'] = transcript
                st.session_state.state['input_processed'] = True
                print(f"DEBUG: Text input processed. Transcript: {transcript[:100]}")

        elif input_method == "Upload audio":
            audio_file_path = process_audio_input(input_method)
            if audio_file_path:
                with st.spinner("Audio wordt verwerkt en getranscribeerd..."):
                    transcript = transcribe_audio(audio_file_path)
                    st.session_state.state['transcript'] = transcript
                    st.session_state.state['input_processed'] = True
                os.unlink(audio_file_path)  # Delete the temporary file
                print(f"DEBUG: Audio processed. Transcript: {transcript[:100]}")
        
        elif input_method in ["Upload audio", "Neem audio op"]:
            audio_file_path = process_audio_input(input_method)
            if audio_file_path:
                with st.spinner("Audio wordt verwerkt en getranscribeerd..."):
                    transcript = st.session_state.state['transcript']  # Get the transcript from the session state
                    st.session_state.state['input_processed'] = True
                os.unlink(audio_file_path)  # Delete the temporary file
                print(f"DEBUG: Audio processed. Transcript: {transcript[:100]}")

        print(f"DEBUG: Input processed: {st.session_state.state['input_processed']}")
        print(f"DEBUG: Transcript available: {bool(st.session_state.state['transcript'])}")

        # Always display the transcript editor, populated with the latest transcript
        st.subheader("Bewerk Transcript")
        edited_transcript = st.text_area(
            "Bewerk het transcript indien nodig:", 
            value=transcript, 
            height=300,
            key='transcript_editor'
        )
        st.session_state.state['edited_transcript'] = edited_transcript
        print(f"DEBUG: Transcript displayed. Edited transcript: {edited_transcript[:100]}")

        if st.button("Analyseer"):
            print("DEBUG: Analyse button clicked")
            with st.spinner("Transcript analyseren..."):
                try:
                    st.session_state.state['suggestions'] = analyze_transcript(edited_transcript)
                    st.session_state.state['analysis_complete'] = True
                    display_success("Analyse voltooid!")
                    print("DEBUG: Analysis complete")
                except Exception as e:
                    display_error(f"Er is een fout opgetreden bij het analyseren van het transcript: {str(e)}")
                    print(f"DEBUG: Error during analysis: {str(e)}")

        if st.session_state.state['analysis_complete']:
            print("DEBUG: Rendering suggestions")
            st.session_state.state['selected_suggestions'] = render_suggestions(st.session_state.state['suggestions'])

            if st.button("Genereer E-mail"):
                print("DEBUG: Generate email button clicked")
                with st.spinner("E-mail genereren..."):
                    try:
                        st.session_state.state['email_content'] = generate_email(
                            edited_transcript,
                            st.session_state.state['selected_suggestions']
                        )
                        st.session_state.state['klantuitvraag'] = st.session_state.state['email_content']
                        update_gesprekslog(edited_transcript, st.session_state.state['email_content'])
                        display_success("E-mail gegenereerd!")
                        print("DEBUG: Email generated")
                    except Exception as e:
                        display_error(f"Er is een fout opgetreden bij het genereren van de e-mail: {str(e)}")
                        print(f"DEBUG: Error generating email: {str(e)}")

        if st.session_state.state['klantuitvraag']:
            print("DEBUG: Displaying klantuitvraag")
            display_klantuitvraag(st.session_state.state['klantuitvraag'])

    st.markdown("---")
    render_conversation_history()
    
    with st.expander("Feedback", expanded=False):
        render_feedback_form()

if __name__ == "__main__":
    main()