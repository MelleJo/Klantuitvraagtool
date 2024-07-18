import streamlit as st
from typing import List, Any

def display_transcript(transcript: str) -> None:
    """Display the generated transcript."""
    st.subheader("Transcript")
    st.text_area("Gegenereerd Transcript:", value=transcript, height=200, key="generated_transcript", disabled=True)

def display_klantuitvraag(klantuitvraag: str) -> None:
    """Display the generated email content."""
    st.subheader("Gegenereerde E-mail")
    st.text_area("E-mail inhoud:", value=klantuitvraag, height=300, key="generated_email")

def display_input_method_selector(input_methods: List[str]) -> str:
    """Display a selector for input methods."""
    return st.selectbox("Selecteer invoermethode:", input_methods, key="input_method_selector")

def display_text_input() -> str:
    """Display a text input area."""
    return st.text_area("Voer tekst in of plak tekst:", height=200, key="text_input")

def display_file_uploader(allowed_types: List[str]) -> Any:
    """Display a file uploader."""
    return st.file_uploader("Upload een bestand:", type=allowed_types, key="file_uploader")

def display_generate_button(label: str = "Genereer") -> bool:
    """Display a generate button."""
    return st.button(label, key=f"generate_button_{label}")

def display_progress_bar(progress: float) -> None:
    """Display a progress bar."""
    st.progress(progress, key="progress_bar")

def display_spinner(text: str) -> Any:
    """Display a spinner with custom text."""
    return st.spinner(text)

def display_success(message: str) -> None:
    """Display a success message."""
    st.success(message)

def display_error(message: str) -> None:
    """Display an error message."""
    st.error(message)

def display_warning(message: str) -> None:
    """Display a warning message."""
    st.warning(message)

def display_metric(label: str, value: Any) -> None:
    """Display a metric with a label and value."""
    st.markdown(f"""
    <div class="metric-container">
        <p style='font-size: 14px; color: #555; margin-bottom: 5px;'>{label}</p>
        <p style='font-size: 20px; font-weight: bold; margin: 0;'>{value}</p>
    </div>
    """, unsafe_allow_html=True)

def display_expandable_text(label: str, content: str) -> None:
    """Display expandable text content."""
    with st.expander(label):
        st.markdown(content)

def display_checkbox(label: str, key: str) -> bool:
    """Display a checkbox with a custom label and key."""
    return st.checkbox(label, key=key)

def display_radio_buttons(label: str, options: List[str], key: str) -> str:
    """Display radio buttons with a custom label, options, and key."""
    return st.radio(label, options, key=key)

def display_multiselect(label: str, options: List[str], key: str) -> List[str]:
    """Display a multiselect widget with a custom label, options, and key."""
    return st.multiselect(label, options, key=key)

def display_date_input(label: str, key: str) -> Any:
    """Display a date input widget with a custom label and key."""
    return st.date_input(label, key=key)

def display_time_input(label: str, key: str) -> Any:
    """Display a time input widget with a custom label and key."""
    return st.time_input(label, key=key)