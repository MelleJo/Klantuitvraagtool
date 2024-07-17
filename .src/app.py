import streamlit as st
from ui.pages import (
    render_input_step, 
    render_analysis_step, 
    render_recommendations_step, 
    render_client_report_step,
    render_feedback_form,
    render_conversation_history
)
from utils.session_state import initialize_session_state
from utils.styles import apply_custom_css

# Set page config at the very beginning
st.set_page_config(page_title="Klantuitvraagtool", page_icon="🔒", layout="wide")

def load_config():
    return {
        "INPUT_METHODS": ["Voer tekst in of plak tekst", "Upload tekst", "Upload audio", "Neem audio op"],
    }

def main():
    apply_custom_css()
    st.title("🔒 Klantuitvraagtool v0.0.3")
    
    config = load_config()
    initialize_session_state()

    steps = ["Input Data", "Analyze", "Recommendations", "Client Report"]
    
    cols = st.columns(4)
    for i, step in enumerate(steps, 1):
        with cols[i-1]:
            if st.session_state.state['active_step'] == i:
                st.markdown(f"<div style='text-align: center; font-weight: bold; color: #4CAF50;'>{i}. {step}</div>", unsafe_allow_html=True)
            elif st.session_state.state['active_step'] > i:
                st.markdown(f"<div style='text-align: center; text-decoration: line-through;'>{i}. {step}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: center;'>{i}. {step}</div>", unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.state['active_step'] == 1:
        render_input_step(config)
    elif st.session_state.state['active_step'] == 2:
        render_analysis_step()
    elif st.session_state.state['active_step'] == 3:
        render_recommendations_step()
    elif st.session_state.state['active_step'] == 4:
        render_client_report_step()

    st.markdown("---")
    render_conversation_history()
    
    with st.expander("Feedback", expanded=False):
        render_feedback_form()

if __name__ == "__main__":
    main()