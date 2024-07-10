import streamlit as st
from services.email_service import send_feedback_email
import html

def render_feedback_form():
    with st.form(key="feedback_form"):
        user_first_name = st.text_input("Uw voornaam (verplicht bij feedback):")
        feedback = st.radio("Was deze klantuitvraag nuttig?", ["Positief", "Negatief"])
        additional_feedback = st.text_area("Laat aanvullende feedback achter:")
        submit_button = st.form_submit_button(label="Verzend feedback")

        if submit_button:
            if not user_first_name:
                st.warning("Voornaam is verplicht bij het geven van feedback.", icon="⚠️")
            else:
                success = send_feedback_email(
                    transcript=st.session_state.get('transcript', ''),
                    klantuitvraag=st.session_state.get('klantuitvraag', ''),
                    feedback=feedback,
                    additional_feedback=additional_feedback,
                    user_first_name=user_first_name
                )
                if success:
                    st.success("Bedankt voor uw feedback!")
                else:
                    st.error("Er is een fout opgetreden bij het verzenden van de feedback. Probeer het later opnieuw.")

def render_conversation_history():
    st.subheader("Laatste vijf gesprekken")
    for i, gesprek in enumerate(st.session_state.get('gesprekslog', [])):
        with st.expander(f"Gesprek {i+1} op {gesprek['time']}"):
            st.markdown("**Transcript:**")
            st.markdown(f'<div class="content">{html.escape(gesprek["transcript"])}</div>', unsafe_allow_html=True)
            st.markdown("**Gegenereerde E-mail:**")
            st.markdown(gesprek["klantuitvraag"], unsafe_allow_html=True)

def render_suggestions(suggestions):
    st.subheader("Verzekeringsvoorstellen")
    for i, suggestion in enumerate(suggestions):
        key = f"suggestion_{i}"
        if key not in st.session_state:
            st.session_state[key] = suggestion.get('selected', False)
        
        suggestion['selected'] = st.checkbox(
            suggestion['titel'],
            value=st.session_state[key],
            key=key,
            help=suggestion['redenering'],
            on_change=update_suggestion_state,
            args=(key,)
        )

def update_suggestion_state(key):
    st.session_state[key] = not st.session_state[key]

print("ui/pages.py loaded successfully")