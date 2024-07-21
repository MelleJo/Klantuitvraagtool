import streamlit as st
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

# Set page config at the very beginning
st.set_page_config(page_title="Klantuitvraagtool", page_icon="🔒", layout="wide")

def load_config() -> Dict[str, Any]:
    """Load and return the application configuration."""
    return {
        "INPUT_METHODS": ["Voer tekst in of plak tekst", "Upload tekst", "Upload audio", "Neem audio op"],
    }

def render_navigation():
    """Render navigation buttons."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.state['active_step'] > 1:
            if st.button("⬅️ Vorige", key="previous_button"):
                st.session_state.state['active_step'] -= 1
                st.rerun()

    with col3:
        if st.session_state.state['active_step'] < 4:
            if st.button("Volgende ➡️", key="next_button"):
                st.session_state.state['active_step'] += 1
                st.rerun()

def render_progress_bar(active_step: int) -> None:
    """Render the progress bar for the current step."""
    steps = ["Input Data", "Analyze", "Recommendations", "Client Report"]
    cols = st.columns(4)
    for i, step in enumerate(steps, 1):
        with cols[i-1]:
            if active_step == i:
                st.markdown(f"<div class='step active'>{i}. {step}</div>", unsafe_allow_html=True)
            elif active_step > i:
                st.markdown(f"<div class='step completed'>{i}. {step}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='step'>{i}. {step}</div>", unsafe_allow_html=True)

def main() -> None:
    """Main function to run the Streamlit app."""
    try:
        # Apply the improved UI styling
        ImprovedUIStyled()
        
        st.title("🔒 Klantuitvraagtool v0.0.5")
        
        config = load_config()
        initialize_session_state()

        render_progress_bar(st.session_state.state['active_step'])

        st.markdown("---")

        if st.session_state.state['active_step'] == 1:
            render_input_step(config)
        elif st.session_state.state['active_step'] == 2:
            render_analysis_step()
        elif st.session_state.state['active_step'] == 3:
            render_recommendations_step()
        elif st.session_state.state['active_step'] == 4:
            render_client_report_step()

        render_navigation()

        st.markdown("---")
        render_conversation_history()
        
        with st.expander("Feedback", expanded=False):
            render_feedback_form()

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.error("Please refresh the page and try again. If the problem persists, contact support.")

if __name__ == "__main__":
    main()