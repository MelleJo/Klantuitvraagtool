import streamlit as st
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
    selected_suggestions = []

    for i, suggestion in enumerate(suggestions):
        with st.expander(f"Recommendation {i+1}: {suggestion['title']}"):
            st.write(f"**Description:** {suggestion['description']}")
            st.write(f"**Justification:** {suggestion['justification']}")
            st.write(f"**Specific Risks:** {suggestion['specific_risks']}")
            is_selected = st.checkbox("Select this recommendation", key=f"rec_{i}")
            if is_selected:
                selected_suggestions.append(suggestion)

    return selected_suggestions