import streamlit as st

def initialize_session_state():
    if 'state' not in st.session_state:
        st.session_state.state = {
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