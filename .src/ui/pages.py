import streamlit as st
from services.email_service import send_feedback_email
import html
import xml.etree.ElementTree as ET
from io import StringIO

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



import streamlit as st
import xml.etree.ElementTree as ET

def render_suggestions(suggestions):
    st.subheader("Verzekeringsvoorstellen")
    
    if 'suggestion_states' not in st.session_state:
        st.session_state.suggestion_states = {}

    selected_suggestions = []

    if isinstance(suggestions, str):
        try:
            root = ET.fromstring(suggestions)
            
            st.markdown("### Bestaande Dekking")
            bestaande_dekking = root.find('bestaande_dekking').text.strip()
            st.write(bestaande_dekking)
            
            st.markdown("### Dekkingshiaten")
            dekkingshiaten = root.find('dekkingshiaten').text.strip().split('-')
            for hiaat in dekkingshiaten:
                if hiaat.strip():
                    st.write(f"- {hiaat.strip()}")
            
            st.markdown("### Verzekeringsaanbevelingen")
            for i, aanbeveling in enumerate(root.find('verzekeringsaanbevelingen').findall('aanbeveling')):
                title = aanbeveling.text.strip()
                key = f"suggestion_{i}"
                
                if key not in st.session_state.suggestion_states:
                    st.session_state.suggestion_states[key] = False

                is_selected = st.checkbox(title, key=key)
                st.session_state.suggestion_states[key] = is_selected

                if is_selected:
                    selected_suggestions.append(aanbeveling)

                rechtvaardiging = aanbeveling.find('rechtvaardiging').text.strip()
                st.markdown("**Rechtvaardiging:**")
                st.write(rechtvaardiging)
                
                risicos = aanbeveling.find('bedrijfsspecifieke_risicos').text.strip()
                st.markdown("**Bedrijfsspecifieke risico's:**")
                st.write(risicos)
                
                st.write("---")
            
            st.markdown("### Aanvullende Opmerkingen")
            opmerkingen = root.find('aanvullende_opmerkingen').text.strip().split('\n')
            for opmerking in opmerkingen:
                if opmerking.strip():
                    st.write(f"- {opmerking.strip()}")
        
        except ET.ParseError as e:
            st.error(f"Er is een fout opgetreden bij het verwerken van de suggesties: {str(e)}")
            st.write("Ruwe suggesties:")
            st.write(suggestions)
    else:
        st.error("Onverwacht type voor suggesties. Verwacht een string.")
    
    return selected_suggestions