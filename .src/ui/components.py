import streamlit as st
import html

def setup_page_style():
    st.set_page_config(page_title="Klantuitvraagtool", page_icon="🎙️", layout="wide")
    st.markdown("""
    <style>
    .main {
        background-color: #f0f8ff;
        color: #333;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 12px 28px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 30px;
        transition: all 0.3s ease 0s;
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 15px 20px rgba(46, 229, 157, 0.4);
        transform: translateY(-7px);
    }
    .klantuitvraag-box, .transcript-box {
        border: none;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        background-color: #ffffff;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .klantuitvraag-box:hover, .transcript-box:hover {
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
        transform: translateY(-5px);
    }
    .klantuitvraag-box h3, .transcript-box h3 {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
        margin-bottom: 20px;
        text-align: center;
        font-weight: 600;
    }
    .content {
        white-space: pre-wrap;
        word-wrap: break-word;
        font-size: 16px;
        line-height: 1.8;
        color: #34495e;
    }
    </style>
    """, unsafe_allow_html=True)

def display_transcript(transcript):
    if transcript:
        with st.expander("Toon Transcript", expanded=False):
            st.markdown('<div class="transcript-box">', unsafe_allow_html=True)
            st.markdown('<h3>Transcript</h3>', unsafe_allow_html=True)
            st.markdown(f'<div class="content">{html.escape(transcript)}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

def display_klantuitvraag(klantuitvraag):
    if klantuitvraag:
        st.markdown('<div class="klantuitvraag-box">', unsafe_allow_html=True)
        st.markdown('<h3>Klantuitvraag</h3>', unsafe_allow_html=True)
        st.markdown(f'<div class="content">{html.escape(klantuitvraag)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def display_input_method_selector(input_methods):
    return st.radio("Wat wil je laten verwerken?", input_methods, key='input_method_radio')

def display_text_input():
    return st.text_area("Voeg tekst hier in:", 
                        value=st.session_state.get('input_text', ''), 
                        height=300,
                        key='input_text_area')

def display_file_uploader(file_types):
    return st.file_uploader("Kies een bestand", type=file_types)

def display_generate_button():
    return st.button("Genereer klantuitvraag", key='generate_button')

def display_copy_clipboard_button():
    return st.button("Kopieer naar klembord", key='copy_clipboard_button')

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

print("ui/components.py loaded successfully")