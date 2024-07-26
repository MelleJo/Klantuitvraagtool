import streamlit as st
from typing import Dict, Any, List
import simplejson as json

def initialize_session_state() -> None:
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
    return st.session_state.state

def update_session_state(key: str, value: Any) -> None:
    st.session_state.state[key] = value

def reset_session_state() -> None:
    initialize_session_state()

def add_to_conversation_history(transcript: str, klantuitvraag: str) -> None:
    if 'gesprekslog' not in st.session_state.state:
        st.session_state.state['gesprekslog'] = []
    
    st.session_state.state['gesprekslog'].append({
        'time': st.session_state.get('current_time', 'Onbekende tijd'),
        'transcript': transcript,
        'klantuitvraag': klantuitvraag
    })
    
    # Bewaar alleen de laatste 5 gesprekken
    st.session_state.state['gesprekslog'] = st.session_state.state['gesprekslog'][-5:]

def get_conversation_history() -> List[Dict[str, str]]:
    return st.session_state.state.get('gesprekslog', [])

def clear_step_data(step: int) -> None:
    if step == 1:
        st.session_state.state['transcript'] = ''
        st.session_state.state['input_processed'] = False
        st.session_state.state['transcription_complete'] = False
    elif step == 2:
        st.session_state.state['suggestions'] = []
        st.session_state.state['analysis_complete'] = False
    elif step == 3:
        st.session_state.state['selected_suggestions'] = []
    # Removed clearing of email_content when moving to step 4
    # elif step == 4:
    #     st.session_state.state['email_content'] = ''

def move_to_step(step: int) -> None:
    current_step = st.session_state.state['active_step']
    if step != current_step:
        st.session_state.state['active_step'] = step
        for i in range(step + 1, 5):
            clear_step_data(i)
        st.experimental_rerun()