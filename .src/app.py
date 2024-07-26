import streamlit as st
import simplejson as json
from typing import Dict, Any
from ui.pages import (
    render_input_step,
    render_analysis_step,
    render_recommendations_step,
    render_client_report_step,
    render_feedback_form,
    render_conversation_history
)
from utils.session_state import initialize_session_state, update_session_state
from ui.components import ImprovedUIStyled

# Stel de pagina-configuratie in aan het begin
st.set_page_config(
    page_title="Klantuitvraagtool",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Definieer een kleurenschema
COLOR_THEME = {
    "primary": "#1E40AF",
    "secondary": "#3B82F6",
    "background": "#F3F4F6",
    "text": "#1F2937",
    "accent": "#10B981"
}

# Initialize session state if not already done
if 'state' not in st.session_state:
    initialize_session_state()

def load_config() -> Dict[str, Any]:
    """Laad en retourneer de applicatieconfiguratie."""
    return {
        "INPUT_METHODS": ["Voer tekst in of plak tekst", "Upload tekstbestand", "Upload audiobestand", "Neem audio op"],
    }

def render_navigation():
    """Toon navigatieknoppen."""
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.session_state.state['active_step'] > 1:
            if st.button("⬅️ Vorige", key="previous_button", use_container_width=True):
                st.session_state.state['active_step'] -= 1
                st.rerun()

    with col3:
        if st.session_state.state['active_step'] < 4:
            if st.button("Volgende ➡️", key="next_button", use_container_width=True):
                st.session_state.state['active_step'] += 1
                st.rerun()

def render_progress_bar(active_step: int) -> None:
    """Toon de voortgangsbalk voor de huidige stap."""
    steps = ["Gegevens invoeren", "Analyseren", "Aanbevelingen", "Klantrapport"]
    
    st.markdown(
        f"""
        <style>
            .stProgress > div > div > div > div {{
                background-color: {COLOR_THEME['secondary']};
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
    st.progress(active_step / len(steps))

def main():
    config = load_config()
    st.sidebar.title("Klantuitvraagtool")
    
    # UI component for improved styling
    ImprovedUIStyled()

    # Render the main steps based on the current active step in session state
    step_functions = [
        render_input_step,
        render_analysis_step,
        render_recommendations_step,
        render_client_report_step,
        render_feedback_form,
        render_conversation_history
    ]

    if 'active_step' not in st.session_state:
        st.session_state.active_step = 0

    active_step = st.session_state.active_step
    step_functions[active_step]()

    # Render navigation and progress bar
    render_navigation()
    render_progress_bar(active_step)

if __name__ == "__main__":
    main()
