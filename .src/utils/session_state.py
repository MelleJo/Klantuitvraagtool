import streamlit as st
from typing import Dict, Any, List

def initialize_session_state() -> None:
    """Initialize the session state with default values if not already set."""
    if 'state' not in st.session_state:
        st.session_state.state: Dict[str, Any] = {
            'transcript': '',
            'edited_transcript': '',
            'klantuitvraag': '',
            'klantuitvraag_versions': [],
            'current_version_index': -1,
            'input_text': '',
            'gesprekslog': [],
            'product_info': '',
            'selected_products': [],
            'suggestions': [],
            'selected_suggestions': [],
            'email_content': '',
            'input_processed': False,
            'analysis_complete': False,
            'transcription_complete': False,
            'active_step': 1,
        }
    elif 'active_step' not in st.session_state.state:
        st.session_state.state['active_step'] = 1

def get_session_state() -> Dict[str, Any]:
    """Get the current session state."""
    return st.session_state.state

def update_session_state(key: str, value: Any) -> None:
    """Update a specific key in the session state."""
    st.session_state.state[key] = value

def reset_session_state() -> None:
    """Reset the session state to its initial values."""
    initialize_session_state()

def add_to_conversation_history(transcript: str, klantuitvraag: str) -> None:
    """Add a new conversation to the history."""
    if 'gesprekslog' not in st.session_state.state:
        st.session_state.state['gesprekslog'] = []
    
    st.session_state.state['gesprekslog'].append({
        'time': st.session_state.get('current_time', 'Unknown time'),
        'transcript': transcript,
        'klantuitvraag': klantuitvraag
    })
    
    # Keep only the last 5