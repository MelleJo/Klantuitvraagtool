import streamlit as st
from typing import Dict, Any, List

def initialize_session_state() -> None:
    if 'transcript' not in st.session_state:
        st.session_state.transcript = ''
    if 'edited_transcript' not in st.session_state:
        st.session_state.edited_transcript = ''
    if 'klantuitvraag' not in st.session_state:
        st.session_state.klantuitvraag = ''
    if 'klantuitvraag_versions' not in st.session_state:
        st.session_state.klantuitvraag_versions = []
    if 'current_version_index' not in st.session_state:
        st.session_state.current_version_index = -1
    if 'input_text' not in st.session_state:
        st.session_state.input_text = ''
    if 'gesprekslog' not in st.session_state:
        st.session_state.gesprekslog = []
    if 'product_info' not in st.session_state:
        st.session_state.product_info = ''
    if 'selected_products' not in st.session_state:
        st.session_state.selected_products = []
    if 'suggestions' not in st.session_state:
        st.session_state.suggestions = []
    if 'selected_suggestions' not in st.session_state:
        st.session_state.selected_suggestions = []
    if 'email_content' not in st.session_state:
        st.session_state.email_content = ''
    if 'input_processed' not in st.session_state:
        st.session_state.input_processed = False
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'transcription_complete' not in st.session_state:
        st.session_state.transcription_complete = False
    if 'active_step' not in st.session_state:
        st.session_state.active_step = 1
    if 'last_input_hash' not in st.session_state:
        st.session_state.last_input_hash = None

def get_session_state() -> Dict[str, Any]:
    return st.session_state

def update_session_state(key: str, value: Any) -> None:
    setattr(st.session_state, key, value)

def reset_session_state() -> None:
    initialize_session_state()

def add_to_conversation_history(transcript: str, klantuitvraag: str) -> None:
    if 'gesprekslog' not in st.session_state:
        st.session_state.gesprekslog = []
    
    st.session_state.gesprekslog.append({
        'time': st.session_state.get('current_time', 'Onbekende tijd'),
        'transcript': transcript,
        'klantuitvraag': klantuitvraag
    })
    
    # Keep only the last 5 conversations
    st.session_state.gesprekslog = st.session_state.gesprekslog[-5:]

def get_conversation_history() -> List[Dict[str, str]]:
    return st.session_state.get('gesprekslog', [])

def clear_step_data(step: int) -> None:
    if step == 1:
        st.session_state.transcript = ''
        st.session_state.input_processed = False
        st.session_state.transcription_complete = False
    elif step == 2:
        st.session_state.suggestions = []
        st.session_state.analysis_complete = False
    elif step == 3:
        st.session_state.selected_suggestions = []
    elif step == 4:
        st.session_state.email_content = ''

def move_to_step(step: int) -> None:
    current_step = st.session_state.active_step
    if step != current_step:
        st.session_state.active_step = step
        for i in range(step + 1, 5):
            clear_step_data(i)

def clear_analysis_results():
    st.session_state.suggestions = []
    st.session_state.selected_suggestions = []
    st.session_state.email_content = ''
    st.session_state.analysis_complete = False