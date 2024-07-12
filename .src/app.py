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
            'transcript': "",
            'edited_transcript': "",
            'klantuitvraag': "",
            'klantuitvraag_versions': [],
            'current_version_index': -1,
            'input_text': "",
            'gesprekslog': [],
            'product_info': "",
            'selected_products': [],
            'suggestions': [],
            'selected_suggestions': [],
            'email_content': "",
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
        print(f"Selected input method: {input_method}")

    with col2:
        st.markdown("### 📝 Transcript & Klantuitvraag")
        if input_method == "Upload tekst":
            uploaded_file = display_file_uploader(['txt', 'docx', 'pdf'])
            if uploaded_file:
                st.session_state.state['transcript'] = process_uploaded_file(uploaded_file)
                st.session_state.state['input_processed'] = True
                display_success("Bestand succesvol geüpload en verwerkt.")
                print("Text file processed. Transcript:", st.session_state.state['transcript'][:100])

        elif input_method == "Voer tekst in of plak tekst":
            input_text = display_text_input()
            if display_generate_button():
                st.session_state.state['transcript'] = input_text
                st.session_state.state['input_processed'] = True
                print("Text input processed. Transcript:", st.session_state.state['transcript'][:100])

        elif input_method in ["Upload audio", "Neem audio op"]:
            audio_data = process_audio_input(input_method)
            if audio_data:
                with st.spinner("Audio wordt verwerkt en getranscribeerd..."):
                    st.session_state.state['transcript'] = transcribe_audio(audio_data)
                    st.session_state.state['input_processed'] = True
                display_success("Audio succesvol verwerkt en getranscribeerd.")
                print("Audio processed. Transcript:", st.session_state.state['transcript'][:100])

        print("Input processed:", st.session_state.state['input_processed'])
        print("Transcript available:", bool(st.session_state.state['transcript']))
        print("Transcript content:", st.session_state.state['transcript'][:100])

        # Always attempt to display the transcript
        st.subheader("Transcript")
        st.session_state.state['edited_transcript'] = st.text_area(
            "Bewerk het transcript indien nodig:", 
            value=st.session_state.state['transcript'], 
            height=300,
            key='transcript_editor'
        )
        print("Transcript displayed")

        if st.button("Analyseer"):
            print("Analyse button clicked")
            with st.spinner("Transcript analyseren..."):
                try:
                    st.session_state.state['suggestions'] = analyze_transcript(st.session_state.state['edited_transcript'])
                    st.session_state.state['analysis_complete'] = True
                    display_success("Analyse voltooid!")
                    print("Analysis complete")
                except Exception as e:
                    display_error(f"Er is een fout opgetreden bij het analyseren van het transcript: {str(e)}")
                    print(f"Error during analysis: {str(e)}")

        if st.session_state.state['analysis_complete']:
            print("Rendering suggestions")
            st.session_state.state['selected_suggestions'] = render_suggestions(st.session_state.state['suggestions'])

            if st.button("Genereer E-mail"):
                print("Generate email button clicked")
                with st.spinner("E-mail genereren..."):
                    try:
                        st.session_state.state['email_content'] = generate_email(
                            st.session_state.state['edited_transcript'],
                            st.session_state.state['selected_suggestions']
                        )
                        st.session_state.state['klantuitvraag'] = st.session_state.state['email_content']
                        update_gesprekslog(st.session_state.state['edited_transcript'], st.session_state.state['email_content'])
                        display_success("E-mail gegenereerd!")
                        print("Email generated")
                    except Exception as e:
                        display_error(f"Er is een fout opgetreden bij het genereren van de e-mail: {str(e)}")
                        print(f"Error generating email: {str(e)}")

        if st.session_state.state['klantuitvraag']:
            print("Displaying klantuitvraag")
            display_klantuitvraag(st.session_state.state['klantuitvraag'])

    st.markdown("---")
    render_conversation_history()
    
    with st.expander("Feedback", expanded=False):
        render_feedback_form()

if __name__ == "__main__":
    main()