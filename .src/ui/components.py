import streamlit as st

def setup_page_style():
    st.set_page_config(page_title="Klantuitvraagtool", page_icon="🔒", layout="wide")

def display_transcript(transcript):
    st.subheader("Transcript")
    st.text_area("Gegenereerd Transcript:", value=transcript, height=200, key="generated_transcript", disabled=True)

def display_klantuitvraag(klantuitvraag):
    st.subheader("Gegenereerde E-mail")
    st.text_area("E-mail inhoud:", value=klantuitvraag, height=300)

def display_input_method_selector(input_methods):
    return st.selectbox("Selecteer invoermethode:", input_methods)

def display_text_input():
    return st.text_area("Voer tekst in of plak tekst:", height=200)

def display_file_uploader(allowed_types):
    return st.file_uploader("Upload een bestand:", type=allowed_types)

def display_generate_button():
    return st.button("Genereer")

def display_progress_bar(progress):
    st.progress(progress)

def display_spinner(text):
    with st.spinner(text):
        yield

def display_success(message):
    st.success(message)

def display_error(message):
    st.error(message)

def display_warning(message):
    st.warning(message)