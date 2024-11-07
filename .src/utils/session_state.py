import streamlit as st
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def initialize_session_state() -> None:
    """
    Initialize all required session state variables with default values.
    """
    default_values = {
        # Input processing states
        'transcript': '',
        'edited_transcript': '',
        'input_processed': False,
        'transcription_complete': False,
        
        # Analysis states
        'analysis_complete': False,
        'suggestions': {},
        'selected_suggestions': [],
        'last_input_hash': None,
        
        # Output states
        'email_content': '',
        'corrected_email_content': '',
        
        # Navigation state
        'active_step': 1,
        
        # Conversation history
        'gesprekslog': [],
        
        # Feedback state
        'feedback_submitted': False,
        
        # Recommendations
        'recommendations': [],
        'selected_recommendations': [],
        
        # Insurance details
        'identified_insurances': [],
        'detailed_descriptions': {},
        
        # Form input states
        'feedback_name_input': '',
        'feedback_type_input': 'Positief',
        'feedback_additional_input': '',
    }
    
    # Initialize each state variable if it doesn't exist
    for key, default_value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
            logger.debug(f"Initialized session state: {key}")

def update_session_state(key: str, value: Any) -> None:
    """
    Update a specific session state variable.
    
    Args:
        key (str): The key to update
        value (Any): The new value
    """
    st.session_state[key] = value
    logger.debug(f"Updated session state: {key} = {value}")

def get_session_state() -> Dict[str, Any]:
    """
    Get the current session state as a dictionary.
    
    Returns:
        Dict[str, Any]: Current session state
    """
    return dict(st.session_state)

def reset_session_state() -> None:
    """
    Reset all session state variables to their default values.
    """
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session_state()
    logger.info("Session state reset to defaults")

def add_to_conversation_history(transcript: str, klantuitvraag: str) -> None:
    """
    Add a new conversation to the history.
    
    Args:
        transcript (str): The conversation transcript
        klantuitvraag (str): The generated client inquiry
    """
    if 'gesprekslog' not in st.session_state:
        st.session_state.gesprekslog = []
        
    st.session_state.gesprekslog.append({
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'transcript': transcript,
        'klantuitvraag': klantuitvraag
    })
    
    # Keep only the last 5 conversations
    st.session_state.gesprekslog = st.session_state.gesprekslog[-5:]
    logger.debug("Conversation history updated")

def move_to_step(step: int) -> None:
    """
    Move to a different step in the application flow.
    
    Args:
        step (int): The step number to move to
    """
    if 1 <= step <= 4:  # Ensure step is within valid range
        st.session_state.active_step = step
        logger.info(f"Moved to step {step}")
    else:
        logger.warning(f"Attempted to move to invalid step {step}")

def clear_analysis_results() -> None:
    """
    Clear all analysis-related results from session state.
    """
    analysis_keys = [
        'suggestions',
        'selected_suggestions',
        'email_content',
        'analysis_complete',
        'detailed_descriptions',
        'identified_insurances'
    ]
    
    for key in analysis_keys:
        if key in st.session_state:
            st.session_state[key] = None if key == 'analysis_complete' else {}
    
    logger.debug("Analysis results cleared")