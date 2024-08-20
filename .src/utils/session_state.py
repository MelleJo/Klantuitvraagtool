import streamlit as st
from typing import Dict, Any, List

def initialize_session_state() -> None:
    default_values = {
        'transcript': '',
        'edited_transcript': '',
        'klantuitvraag': '',
        'klantuitvraag_versions': [],
        'current_version_index': -1,
        'input_text': '',
        'gesprekslog': [],  # Make sure this line is present
        'product_info': '',
        'selected_products': [],
        'suggestions': [],
        'selected_suggestions': [],
        'email_content': '',
        'input_processed': False,
        'analysis_complete': False,
        'transcription_complete': False,
        'active_step': 1,
        'last_input_hash': None,
    }
    
    for key, default_value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def get_session_state() -> Dict[str, Any]:
    return dict(st.session_state)

def update_session_state(key: str, value: Any) -> None:
    st.session_state[key] = value

def reset_session_state() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
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