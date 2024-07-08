import os
import sys
import json
import streamlit as st
from openai_service import perform_gpt4_operation
from utils.audio_processing import transcribe_audio, process_audio_input
from utils.file_processing import process_uploaded_file
from services.summarization_service import run_klantuitvraag
from ui.components import display_transcript, display_klantuitvraag
from ui.pages import render_feedback_form, render_conversation_history
from utils.text_processing import update_gesprekslog, load_questions
from st_copy_to_clipboard import st_copy_to_clipboard
from docx import Document
from docx.shared import Pt
from docx.enum.style import WD_STYLE_TYPE
from io import BytesIO
import bleach
import base64
import time

INPUT_METHODS = ["Voer tekst in of plak tekst", "Upload tekst", "Upload audio", "Neem audio op"]

def load_config():
    return {
        "INPUT_METHODS": INPUT_METHODS,
    }

def load_product_descriptions():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'product_descriptions.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        st.error(f"Error loading product descriptions: {str(e)}")
        return {}

def initialize_session_state():
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
    st.set_page_config(page_title="Klantuitvraagtool", page_icon="🎙️", layout="wide")
    
    config = load_config()
    initialize_session_state()
    
    st.title("Klantuivraagtool versie 0.0.1")
    st.markdown("---")

    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("### 📋 Configuratie")
        input_method = st.radio("Invoermethode", config["INPUT_METHODS"], key='input_method_radio')

    with col2:
        st.markdown("### 📝 Transcript & klantuitvraag")
        if input_method == "Upload tekst":
            uploaded_file = st.file_uploader("Kies een bestand", type=['txt', 'docx', 'pdf'])
            if uploaded_file:
                st.session_state.transcript = process_uploaded_file(uploaded_file)
                with st.spinner("Klantuitvraag genereren..."):
                    result = run_klantuitvraag(st.session_state.transcript)
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
                    st.session_state.transcript = st.session_state.input_text
                    
                    with st.spinner("Klantuitvraag genereren..."):
                        result = run_klantuitvraag(st.session_state.transcript)
                    
                    if result["error"] is None:
                        update_klantuitvraag(result["klantuitvraag"])
                        update_gesprekslog(st.session_state.transcript, result["klantuitvraag"])
                        st.success("Klantuitvraag gegenereerd!")
                    else:
                        st.error(f"Er is een fout opgetreden: {result['error']}")
                else:
                    st.warning("Voer alstublieft tekst in om een klantuitvraag te genereren.")

        elif input_method in ["Upload audio", "Neem audio op"]:
            process_audio_input(input_method)

        display_transcript(st.session_state.transcript)

        if st.session_state.klantuitvraag:
            st.markdown("### 📑 Klantuitvraag")
            display_klantuitvraag(st.session_state.klantuitvraag)

    st.markdown("---")
    render_conversation_history()

def update_klantuitvraag(new_klantuitvraag):
    st.session_state.klantuitvraag_versions.append(new_klantuitvraag)
    st.session_state.current_version_index = len(st.session_state.klantuitvraag_versions) - 1
    st.session_state.klantuitvraag = new_klantuitvraag

if __name__ == "__main__":
    product_descriptions = load_product_descriptions()
    main()