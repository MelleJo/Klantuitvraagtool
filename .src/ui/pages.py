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
                    transcript=st.session_state.state.get('transcript', ''),
                    klantuitvraag=st.session_state.state.get('klantuitvraag', ''),
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
    for i, gesprek in enumerate(st.session_state.state.get('gesprekslog', [])):
        with st.expander(f"Gesprek {i+1} op {gesprek['time']}"):
            st.markdown("**Transcript:**")
            st.markdown(f'<div class="content">{html.escape(gesprek["transcript"])}</div>', unsafe_allow_html=True)
            st.markdown("**Gegenereerde E-mail:**")
            st.markdown(gesprek["klantuitvraag"], unsafe_allow_html=True)

def render_suggestions(suggestions):
    st.subheader("Verzekeringsvoorstellen")
    
    # Initialize the suggestions state if it doesn't exist
    if 'suggestion_states' not in st.session_state:
        st.session_state.suggestion_states = {}

    selected_suggestions = []

    for i, suggestion in enumerate(suggestions):
        key = f"suggestion_{i}"
        
        # Initialize the state for this suggestion if it doesn't exist
        if key not in st.session_state.suggestion_states:
            st.session_state.suggestion_states[key] = False

        # Check if suggestion is a dictionary and has a 'titel' key
        if isinstance(suggestion, dict) and 'titel' in suggestion:
            title = suggestion['titel']
            reasoning = suggestion.get('redenering', '')
        else:
            # If suggestion is not in the expected format, use a default title
            title = f"Voorstel {i+1}"
            reasoning = str(suggestion)  # Convert suggestion to string for display

        is_selected = st.checkbox(
            title,
            value=st.session_state.suggestion_states[key],
            key=key,
            help=reasoning
        )

        # Update the state
        st.session_state.suggestion_states[key] = is_selected

        if is_selected:
            selected_suggestions.append(suggestion)

    return selected_suggestions