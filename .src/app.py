import streamlit as st
from ui.pages import (
    render_input_step,
    render_analysis_step,
    render_recommendations_step,
    render_client_report_step,
    render_feedback_form,
    render_conversation_history
)
from utils.session_state import initialize_session_state, update_session_state, move_to_step, clear_analysis_results
from ui.components import ImprovedUIStyled
from ui.checklist import add_checklist_css
import traceback
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Klantuitvraagtool",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

COLOR_THEME = {
    "primary": "#1E40AF",
    "secondary": "#3B82F6",
    "background": "#F3F4F6",
    "text": "#1F2937",
    "accent": "#10B981"
}

def load_config():
    return {
        "INPUT_METHODS": ["Voer tekst in of plak tekst", "Upload tekstbestand", "Upload audiobestand", "Neem audio op"],
    }

def on_previous_click():
    move_to_step(st.session_state.active_step - 1)

def on_next_click():
    if st.session_state.active_step == 1:
        if st.session_state.get('transcript', '').strip():
            move_to_step(st.session_state.active_step + 1)
        else:
            st.error("Voer eerst een geldige tekst in voordat u doorgaat.")
    else:
        move_to_step(st.session_state.active_step + 1)

def render_navigation():
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.session_state.active_step > 1:
            st.button("⬅️ Vorige", key="previous_button", on_click=on_previous_click, use_container_width=True)

    with col3:
        if st.session_state.active_step < 4:
            st.button("Volgende ➡️", key="next_button", on_click=on_next_click, use_container_width=True)

def render_progress_bar(active_step: int):
    steps = ["Gegevens invoeren", "Analyseren", "Aanbevelingen", "Klantrapport"]
    
    progress = (active_step - 1) / (len(steps) - 1)
    st.progress(progress, "Voortgang")
    
    cols = st.columns(len(steps))
    for i, step in enumerate(steps, 1):
        with cols[i-1]:
            if i < active_step:
                st.markdown(f"<p style='color:var(--accent-color);text-align:center;'>{i}. {step}</p>", unsafe_allow_html=True)
            elif i == active_step:
                st.markdown(f"<p style='color:var(--primary-color);font-weight:bold;text-align:center;'>{i}. {step}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color:var(--text-color);text-align:center;'>{i}. {step}</p>", unsafe_allow_html=True)

def main():
    try:
        initialize_session_state()
        ImprovedUIStyled()
        add_checklist_css()
        
        st.markdown(f"""
        <h1 style='text-align: center; color: var(--secondary-color); margin-bottom: 2rem;'>
            🔐 Klantuitvraagtool
        </h1>
        """, unsafe_allow_html=True)
        
        config = load_config()

        render_progress_bar(st.session_state.active_step)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.active_step == 1:
            render_input_step(config)
        elif st.session_state.active_step == 2:
            current_input_hash = hash(st.session_state.get('transcript', ''))
            if current_input_hash != st.session_state.get('last_input_hash'):
                clear_analysis_results()
                st.session_state.last_input_hash = current_input_hash
            render_analysis_step()
        elif st.session_state.active_step == 3:
            render_recommendations_step()
        elif st.session_state.active_step == 4:
            render_client_report_step()

        render_navigation()

        st.markdown("<br><br>", unsafe_allow_html=True)
        
        with st.expander("Gespreksgeschiedenis", expanded=False):
            render_conversation_history()
        
        with st.expander("Feedback", expanded=False):
            render_feedback_form()

    except Exception as e:
        st.error("Er is een onverwachte fout opgetreden.")
        st.error(f"Foutdetails: {str(e)}")
        st.error("Stacktrace:")
        st.code(traceback.format_exc())
        st.error("Vernieuw de pagina en probeer het opnieuw. Als het probleem aanhoudt, neem dan contact op met de ondersteuning.")
        logger.exception("Unexpected error occurred")

if __name__ == "__main__":
    main()