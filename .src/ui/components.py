import streamlit as st

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

def display_generate_button(label="Genereer"):
    return st.button(label)

def display_progress_bar(progress):
    st.progress(progress)

def display_spinner(text):
    return st.spinner(text)

def display_success(message):
    st.success(message)

def display_error(message):
    st.error(message)

def display_warning(message):
    st.warning(message)

def display_metric(label, value):
    st.markdown(f"""
    <div style='padding: 10px; background-color: #f0f2f6; border-radius: 5px; margin-bottom: 10px;'>
        <p style='font-size: 14px; color: #555; margin-bottom: 5px;'>{label}</p>
        <p style='font-size: 20px; font-weight: bold; margin: 0;'>{value}</p>
    </div>
    """, unsafe_allow_html=True)