import streamlit as st
import html

def setup_page_style():
    st.set_page_config(page_title="Klantuitvraagtool", page_icon="🎙️", layout="wide")
    st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
        color: #212529;
        font-family: 'Roboto', sans-serif;
    }
    .stButton > button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    .stButton > button:hover {
        background-color: #0056b3;
    }
    .content-box {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        margin-bottom: 1rem;
    }
    .content-box h3 {
        color: #007bff;
        margin-bottom: 1rem;
    }
    .content {
        white-space: pre-wrap;
        word-wrap: break-word;
        font-size: 1rem;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)

def display_transcript(transcript):
    if transcript:
        with st.expander("Toon Transcript", expanded=False):
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown('<h3>Transcript</h3>', unsafe_allow_html=True)
            st.markdown(f'<div class="content">{html.escape(transcript)}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

def display_klantuitvraag(klantuitvraag):
    if klantuitvraag:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown('<h3>Gegenereerde E-mail</h3>', unsafe_allow_html=True)
        st.markdown(f'<div class="content">{html.escape(klantuitvraag)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def display_input_method_selector(input_methods):
    return st.radio("Hoe wilt u de gegevens invoeren?", input_methods, key='input_method_radio')

def display_text_input():
    return st.text_area("Voer de tekst hier in:", 
                        value=st.session_state.get('input_text', ''), 
                        height=300,
                        key='input_text_area')

def display_file_uploader(file_types):
    return st.file_uploader("Kies een bestand", type=file_types)

def display_generate_button():
    return st.button("Genereer Klantuitvraag", key='generate_button')

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

def display_suggestions(suggestions):
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown('<h3>Verzekeringsvoorstellen</h3>', unsafe_allow_html=True)
    selected_suggestions = []
    for suggestion in suggestions:
        if st.checkbox(suggestion['titel'], help=suggestion['redenering']):
            selected_suggestions.append(suggestion)
    st.markdown('</div>', unsafe_allow_html=True)
    return selected_suggestions

print("ui/components.py loaded successfully")