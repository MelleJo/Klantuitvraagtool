import streamlit as st
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def initialize_session_state() -> None:
    """
    Initialize all required session state variables with default values.
    """
    default_values = {
        # Input and processing states
        'transcript': '',
        'edited_transcript': '',
        'input_text': '',
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
        'detailed_descriptions': {},
        'identified_insurances': [],
        
        # Navigation and UI states
        'active_step': 1,
        'feedback_submitted': False,
        
        # History tracking
        'gesprekslog': [],
        
        # Recommendations state
        'recommendations': [],
        
        # Product information
        'product_info': '',
        'selected_products': []
    }
    
    # Initialize each state variable if it doesn't exist
    for key, default_value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
            logger.debug(f"Initialized session state: {key}")

def get_session_state() -> Dict[str, Any]:
    """
    Get the current session state as a dictionary.
    
    Returns:
        Dict[str, Any]: Current session state
    """
    return dict(st.session_state)

def update_session_state(key: str, value: Any) -> None:
    """
    Update a specific session state variable.
    
    Args:
        key (str): The key to update
        value (Any): The new value
    """
    st.session_state[key] = value
    logger.debug(f"Updated session state: {key}")

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

def get_conversation_history() -> List[Dict[str, str]]:
    """
    Get the conversation history.
    
    Returns:
        List[Dict[str, str]]: List of conversation records
    """
    return st.session_state.get('gesprekslog', [])

def clear_step_data(step: int) -> None:
    """
    Clear data associated with a specific step.
    
    Args:
        step (int): The step number to clear
    """
    if step == 1:
        st.session_state.transcript = ''
        st.session_state.input_processed = False
        st.session_state.transcription_complete = False
    elif step == 2:
        st.session_state.suggestions = {}
        st.session_state.analysis_complete = False
    elif step == 3:
        st.session_state.selected_suggestions = []
    elif step == 4:
        st.session_state.email_content = ''
    
    logger.debug(f"Cleared data for step {step}")

def move_to_step(step: int) -> None:
    """
    Move to a different step in the application flow.
    
    Args:
        step (int): The step number to move to
    """
    current_step = st.session_state.active_step
    if step != current_step:
        st.session_state.active_step = step
        for i in range(step + 1, 5):
            clear_step_data(i)
        logger.info(f"Moved to step {step}")

def clear_analysis_results() -> None:
    """
    Clear all analysis-related results.
    """
    st.session_state.suggestions = {}
    st.session_state.selected_suggestions = []
    st.session_state.email_content = ''
    st.session_state.analysis_complete = False
    logger.debug("Analysis results cleared")