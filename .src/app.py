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
from utils.session_state import initialize_session_state, update_session_state, move_to_step
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
                move_to_step(st.session_state.state['active_step'] - 1)

    with col3:
        if st.session_state.state['active_step'] < 4:
            if st.button("Volgende ➡️", key="next_button", use_container_width=True):
                move_to_step(st.session_state.state['active_step'] + 1)

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
    
    progress = (active_step - 1) / (len(steps) - 1)
    st.progress(progress)
    
    cols = st.columns(len(steps))
    for i, step in enumerate(steps, 1):
        with cols[i-1]:
            if i < active_step:
                st.markdown(f"<p style='color:{COLOR_THEME['accent']};text-align:center;'>{i}. {step}</p>", unsafe_allow_html=True)
            elif i == active_step:
                st.markdown(f"<p style='color:{COLOR_THEME['primary']};font-weight:bold;text-align:center;'>{i}. {step}</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color:{COLOR_THEME['text']};text-align:center;'>{i}. {step}</p>", unsafe_allow_html=True)

def main() -> None:
    """Hoofdfunctie om de Streamlit-app uit te voeren."""
    try:
        # Pas de verbeterde UI-styling toe
        ImprovedUIStyled()
        
        st.markdown(f"""
        <h1 style='text-align: center; color: {COLOR_THEME['primary']}; margin-bottom: 2rem;'>
            🔐 Klantuitvraagtool
        </h1>
        """, unsafe_allow_html=True)
        
        config = load_config()
        initialize_session_state()

        render_progress_bar(st.session_state.state['active_step'])

        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.state['active_step'] == 1:
            render_input_step(config)
        elif st.session_state.state['active_step'] == 2:
            render_analysis_step()
        elif st.session_state.state['active_step'] == 3:
            render_recommendations_step()
        elif st.session_state.state['active_step'] == 4:
            render_client_report_step()

        render_navigation()

        st.markdown("<br><br>", unsafe_allow_html=True)
        
        with st.expander("Gespreksgeschiedenis", expanded=False):
            render_conversation_history()
        
        with st.expander("Feedback", expanded=False):
            render_feedback_form()

    except Exception as e:
        st.error(f"Er is een onverwachte fout opgetreden: {str(e)}")
        st.error("Vernieuw de pagina en probeer het opnieuw. Als het probleem aanhoudt, neem dan contact op met de ondersteuning.")

if __name__ == "__main__":
    main()