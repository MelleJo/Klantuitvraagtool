import streamlit as st
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
st.set_page_config(page_title="Klantuitvraagtool", page_icon="🔒", layout="wide")

def load_config() -> Dict[str, Any]:
    """Laad en retourneer de applicatieconfiguratie."""
    return {
        "INPUT_METHODS": ["Voer tekst in of plak tekst", "Upload tekstbestand", "Upload audiobestand", "Neem audio op"],
    }

def render_navigation():
    """Toon navigatieknoppen."""
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
    """Toon de voortgangsbalk voor de huidige stap."""
    steps = ["Gegevens invoeren", "Analyseren", "Aanbevelingen", "Klantrapport"]
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
    """Hoofdfunctie om de Streamlit-app uit te voeren."""
    try:
        # Pas de verbeterde UI-styling toe
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
        st.error(f"Er is een onverwachte fout opgetreden: {str(e)}")
        st.error("Vernieuw de pagina en probeer het opnieuw. Als het probleem aanhoudt, neem dan contact op met de ondersteuning.")

if __name__ == "__main__":
    main()