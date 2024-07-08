import os
import sys
import traceback
import importlib.util
import json
import streamlit as st
from openai_service import perform_gpt4_operation
from utils.audio_processing import transcribe_audio, process_audio_input
from utils.file_processing import process_uploaded_file
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
print(f"Initial sys.path: {sys.path}")

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
    if hasattr(summarization_service, 'run_klantuitvraag'):
        run_klantuitvraag = summarization_service.run_klantuitvraag
        print("Successfully imported run_klantuitvraag")
    else:
        print("run_klantuitvraag not found in summarization_service")
else:
    print("Failed to import summarization_service")

# Debug import of ui.pages
print("Attempting to import ui.pages")
try:
    from ui.pages import render_feedback_form, render_conversation_history
    print("Successfully imported render_feedback_form and render_conversation_history from ui.pages")
except ImportError as e:
    print(f"Error importing from ui.pages: {str(e)}")
    print("Traceback:")
    traceback.print_exc()
    
    # Try to load the module manually
    ui_pages_path = os.path.join(current_dir, 'ui', 'pages.py')
    ui_pages = debug_import("ui.pages", ui_pages_path)
    
    if ui_pages:
        print("Content of ui.pages:")
        print(dir(ui_pages))
        if hasattr(ui_pages, 'render_conversation_history'):
            render_conversation_history = ui_pages.render_conversation_history
            print("Successfully imported render_conversation_history")
        else:
            print("render_conversation_history not found in ui.pages")
    else:
        print("Failed to import ui.pages")

# Import other necessary modules
print("Importing other modules")
try:
    from ui.components import display_transcript, display_klantuitvraag
    from utils.text_processing import update_gesprekslog, load_questions
    print("All modules imported successfully")
except Exception as e:
    print(f"Error importing modules: {str(e)}")
    print("Traceback:")
    traceback.print_exc()

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
        'selected_products': []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def main():
    print("Entering main function")
    st.set_page_config(page_title="Klantuitvraagtool", page_icon="🎙️", layout="wide")
    
    config = load_config()
    initialize_session_state()
    
    st.title("Klantuitvraagtool versie 0.0.1")
    st.markdown("---")

    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("### 📋 Configuratie")
        input_method = st.radio("Invoermethode", config["INPUT_METHODS"], key='input_method_radio')
        print(f"Selected input method: {input_method}")

    with col2:
        st.markdown("### 📝 Transcript & klantuitvraag")
        if input_method == "Upload tekst":
            uploaded_file = st.file_uploader("Kies een bestand", type=['txt', 'docx', 'pdf'])
            if uploaded_file:
                print(f"File uploaded: {uploaded_file.name}")
                st.session_state.transcript = process_uploaded_file(uploaded_file)
                with st.spinner("Klantuitvraag genereren..."):
                    print("Generating klantuitvraag")
                    result = run_klantuitvraag(st.session_state.transcript)
                print(f"Klantuitvraag generation result: {result}")
                if result["error"] is None:
                    update_klantuitvraag(result["klantuitvraag"])
                    update_gesprekslog(st.session_state.transcript, result["klantuitvraag"])
                    st.success("Klantuitvraag gegenereerd!")
                else:
                    st.error(f"Er is een fout opgetreden: {result['error']}")

        elif input_method == "Voer tekst in of plak tekst":
            st.session_state.input_text = st.text_area("Voer tekst in:", 
                                                       value=st.session_state.input_text, 
                                                       height=200,
                                                       key='input_text_area')
            if st.button("Genereer klantuitvraag", key='generate_button'):
                if st.session_state.input_text:
                    print("Generating klantuitvraag from input text")
                    st.session_state.transcript = st.session_state.input_text
                    
                    with st.spinner("Klantuitvraag genereren..."):
                        result = run_klantuitvraag(st.session_state.transcript)
                    print(f"Klantuitvraag generation result: {result}")
                    if result["error"] is None:
                        update_klantuitvraag(result["klantuitvraag"])
                        update_gesprekslog(st.session_state.transcript, result["klantuitvraag"])
                        st.success("Klantuitvraag gegenereerd!")
                    else:
                        st.error(f"Er is een fout opgetreden: {result['error']}")
                else:
                    st.warning("Voer alstublieft tekst in om een klantuitvraag te genereren.")

        elif input_method in ["Upload audio", "Neem audio op"]:
            print(f"Processing audio input: {input_method}")
            process_audio_input(input_method)

        display_transcript(st.session_state.transcript)

        if st.session_state.klantuitvraag:
            st.markdown("### 📑 Klantuitvraag")
            display_klantuitvraag(st.session_state.klantuitvraag)

    st.markdown("---")
    if 'render_conversation_history' in globals():
        render_conversation_history()
    else:
        print("render_conversation_history is not defined")
        st.error("Unable to render conversation history due to an import error.")

def update_klantuitvraag(new_klantuitvraag):
    print("Updating klantuitvraag")
    st.session_state.klantuitvraag_versions.append(new_klantuitvraag)
    st.session_state.current_version_index = len(st.session_state.klantuitvraag_versions) - 1
    st.session_state.klantuitvraag = new_klantuitvraag

if __name__ == "__main__":
    print("Starting main execution")
    product_descriptions = load_product_descriptions()
    main()
    print("Finished main execution")