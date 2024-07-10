import os
import sys
import traceback
import importlib.util
import json
import streamlit as st
from openai_service import perform_gpt4_operation
from utils.audio_processing import transcribe_audio, process_audio_input
from utils.file_processing import process_uploaded_file
from utils.text_processing import update_gesprekslog, load_questions
from st_copy_to_clipboard import st_copy_to_clipboard
from docx import Document
from docx.shared import Pt
from docx.enum.style import WD_STYLE_TYPE
from io import BytesIO
import bleach
import base64
import time

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

def debug_import(module_name, file_path):
    print(f"Attempting to import {module_name} from {file_path}")
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"Successfully imported {module_name}")
        print(f"Content of {module_name}:")
        print(dir(module))
        return module
    except Exception as e:
        print(f"Error importing {module_name}: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        try:
            with open(file_path, 'r') as f:
                print(f"Content of {file_path}:")
                print(f.read())
        except Exception as file_error:
            print(f"Error reading {file_path}: {str(file_error)}")
        return None

# Debug import of summarization_service
summarization_service_path = os.path.join(current_dir, 'services', 'summarization_service.py')
summarization_service = debug_import("summarization_service", summarization_service_path)

if summarization_service:
    print("Attempting to access run_klantuitvraag")
    print(f"Debug: Input text being sent to run_klantuitvraag: {st.session_state.get('transcript', 'No transcript available')}")
    if hasattr(summarization_service, 'run_klantuitvraag'):
        run_klantuitvraag = summarization_service.run_klantuitvraag
        analyze_transcript = summarization_service.analyze_transcript
        generate_email = summarization_service.generate_email
        print("Successfully imported run_klantuitvraag, analyze_transcript, and generate_email")
    else:
        print("Required functions not found in summarization_service")
else:
    print("Failed to import summarization_service")

# Debug import of ui.pages and ui.components
print("Attempting to import UI modules")
try:
    from ui.pages import render_feedback_form, render_conversation_history, render_suggestions
    from ui.components import (
        setup_page_style, display_transcript, display_klantuitvraag,
        display_input_method_selector, display_text_input, display_file_uploader,
        display_generate_button, display_progress_bar, display_spinner,
        display_success, display_error, display_warning
    )
    print("Successfully imported UI modules")
except ImportError as e:
    print(f"Error importing UI modules: {str(e)}")
    print("Traceback:")
    traceback.print_exc()
    
    # Define basic versions of required functions if import fails
    def setup_page_style():
        st.set_page_config(page_title="Klantuitvraagtool", page_icon="🎙️", layout="wide")
    
    def display_transcript(transcript):
        st.subheader("Transcript")
        st.text_area("", value=transcript, height=200, disabled=True)
    
    def display_klantuitvraag(klantuitvraag):
        st.subheader("Klantuitvraag")
        st.text_area("", value=klantuitvraag, height=200, disabled=True)
    
    def display_input_method_selector(input_methods):
        return st.radio("Selecteer invoermethode:", input_methods)
    
    def display_text_input():
        return st.text_area("Voer tekst in:", height=200)
    
    def display_file_uploader(file_types):
        return st.file_uploader("Upload een bestand", type=file_types)
    
    def display_generate_button():
        return st.button("Genereer")
    
    def display_progress_bar():
        return st.progress(0)
    
    def display_spinner(text):
        return st.spinner(text)
    
    def display_success(text):
        st.success(text)
    
    def display_error(text):
        st.error(text)
    
    def display_warning(text):
        st.warning(text)
    
    def render_feedback_form():
        st.subheader("Feedback")
        st.text_input("Uw naam:")
        st.radio("Was deze klantuitvraag nuttig?", ["Ja", "Nee"])
        st.text_area("Aanvullende opmerkingen:")
        st.button("Verzend feedback")
    
    def render_conversation_history():
        st.subheader("Gespreksgeschiedenis")
        st.text("Geen eerdere gesprekken gevonden.")
    
    def render_suggestions(suggestions):
        st.subheader("Suggesties")
        for suggestion in suggestions:
            st.checkbox(suggestion['title'], help=suggestion['description'])
        return []

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
    print("Initializing session state")
    defaults = {
        'klantuitvraag': "",
        'klantuitvraag_versions': [],
        'current_version_index': -1,
        'input_text': "",
        'transcript': "",
        'gesprekslog': [],
        'product_info': "",
        'selected_products': [],
        'suggestions': [],
        'selected_suggestions': [],
        'email_content': "",
        'input_processed': False,
        'analysis_complete': False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

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
        if input_method == "Upload tekst":
            uploaded_file = display_file_uploader(['txt', 'docx', 'pdf'])
            if uploaded_file:
                st.session_state['transcript'] = process_uploaded_file(uploaded_file)
                st.session_state['input_processed'] = True
                display_success("Bestand succesvol geüpload en verwerkt.")

        elif input_method == "Voer tekst in of plak tekst":
            st.session_state['transcript'] = display_text_input()
            if display_generate_button():
                st.session_state['input_processed'] = True

        elif input_method in ["Upload audio", "Neem audio op"]:
            audio_data = process_audio_input(input_method)
            if audio_data:
                with st.spinner("Audio wordt verwerkt en getranscribeerd..."):
                    st.session_state['transcript'] = transcribe_audio(audio_data)
                    st.session_state['input_processed'] = True
                display_success("Audio succesvol verwerkt en getranscribeerd.")

        if st.session_state.get('input_processed', False):
            display_transcript(st.session_state['transcript'])
            st.session_state['edited_transcript'] = st.text_area(
                "Bewerk het transcript indien nodig:", 
                value=st.session_state['transcript'], 
                height=300
            )

            if st.button("Analyseer"):
                with st.spinner("Transcript analyseren..."):
                    st.session_state['suggestions'] = analyze_transcript(st.session_state['edited_transcript'])
                st.session_state['analysis_complete'] = True

            if st.session_state.get('analysis_complete', False):
                st.session_state['selected_suggestions'] = render_suggestions(st.session_state['suggestions'])

                if st.button("Genereer E-mail"):
                    with st.spinner("E-mail genereren..."):
                        st.session_state['email_content'] = generate_email(
                            st.session_state['edited_transcript'],
                            st.session_state['selected_suggestions']
                        )
                    st.session_state['klantuitvraag'] = st.session_state['email_content']
                    update_gesprekslog(st.session_state['edited_transcript'], st.session_state['email_content'])
                    display_success("E-mail gegenereerd!")

            if st.session_state.get('klantuitvraag'):
                display_klantuitvraag(st.session_state['klantuitvraag'])

        # Existing klantuitvraag generation logic
        if not st.session_state.get('analysis_complete', False) and st.session_state.get('input_processed', False):
            if st.button("Genereer Klantuitvraag (Oude Methode)"):
                with st.spinner("Klantuitvraag genereren..."):
                    result = run_klantuitvraag(st.session_state['edited_transcript'])
                if result["error"] is None:
                    st.session_state['klantuitvraag'] = result["klantuitvraag"]
                    update_gesprekslog(st.session_state['edited_transcript'], result["klantuitvraag"])
                    display_success("Klantuitvraag gegenereerd!")
                else:
                    display_error(f"Er is een fout opgetreden: {result['error']}")

    st.markdown("---")
    render_conversation_history()
    
    with st.expander("Feedback", expanded=False):
        render_feedback_form()

if __name__ == "__main__":
    main()